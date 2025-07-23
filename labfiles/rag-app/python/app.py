import os
import json
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from openai import AzureOpenAI
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Configuration
OPEN_AI_ENDPOINT = os.getenv("OPEN_AI_ENDPOINT")
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
SEARCH_URL = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

# Initialize Azure OpenAI client
chat_client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=OPEN_AI_ENDPOINT,
    api_key=OPEN_AI_KEY
)

def get_chat_session():
    """Get or create chat session"""
    if 'chat_id' not in session:
        session['chat_id'] = str(uuid.uuid4())
        session['messages'] = [
            {"role": "system", "content": "You are a friendly travel assistant for Margie's Travel. You help customers find the perfect travel experiences using our comprehensive travel database. Be helpful, enthusiastic, and provide detailed information about destinations, accommodations, and travel services."}
        ]
    return session['messages']

def create_rag_params():
    """Create RAG parameters for Azure AI Search integration"""
    return {
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": SEARCH_URL,
                    "index_name": INDEX_NAME,
                    "authentication": {
                        "type": "api_key",
                        "key": SEARCH_KEY,
                    },
                    "query_type": "simple",  # Use simple query type for now
                    "in_scope": True,
                    "strictness": 3,
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": EMBEDDING_MODEL,
                    }
                }
            }
        ],
    }

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        print(f"🔍 DEBUG: User message: {user_message}")
        
        # Get chat session
        messages = get_chat_session()
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        # Create RAG parameters
        rag_params = create_rag_params()
        print(f"🔍 DEBUG: RAG params: {rag_params}")
        
        # Get response from Azure OpenAI with RAG
        response = chat_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            extra_body=rag_params,
            max_tokens=1000,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        print(f"🔍 DEBUG: Assistant response: {assistant_message}")
        
        # Check if there are citations or context sources
        if hasattr(response.choices[0].message, 'context') and response.choices[0].message.context:
            print(f"🔍 DEBUG: Context found: {response.choices[0].message.context}")
        
        # Add assistant response to conversation history
        messages.append({"role": "assistant", "content": assistant_message})
        
        # Update session
        session['messages'] = messages
        
        return jsonify({
            'response': assistant_message,
            'chat_id': session['chat_id']
        })
        
    except Exception as e:
        print(f"❌ ERROR in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Sorry, I encountered an error: {str(e)}'}), 500

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    try:
        session.pop('chat_id', None)
        session.pop('messages', None)
        return jsonify({'success': True, 'message': 'Chat history cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get chat history"""
    try:
        messages = session.get('messages', [])
        # Filter out system messages for the UI
        user_messages = [msg for msg in messages if msg['role'] in ['user', 'assistant']]
        return jsonify({
            'messages': user_messages,
            'chat_id': session.get('chat_id')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Margie\'s Travel RAG App'})

@app.route('/api/test-search', methods=['GET'])
def test_search():
    """Test Azure AI Search connectivity"""
    try:
        import requests
        
        # Test Azure AI Search directly
        headers = {
            'Content-Type': 'application/json',
            'api-key': SEARCH_KEY
        }
        
        # Simple search test
        search_url = f"{SEARCH_URL}/indexes/{INDEX_NAME}/docs"
        params = {
            'api-version': '2021-04-30-Preview',
            'search': 'Dubai',
            'top': 3
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        search_results = response.json()
        
        print(f"🔍 SEARCH TEST: Status {response.status_code}")
        print(f"🔍 SEARCH RESULTS: {search_results}")
        
        return jsonify({
            'status': 'success',
            'search_endpoint': SEARCH_URL,
            'index_name': INDEX_NAME,
            'results_count': search_results.get('value', []),
            'search_response': search_results
        })
        
    except Exception as e:
        print(f"❌ SEARCH TEST ERROR: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'search_endpoint': SEARCH_URL,
            'index_name': INDEX_NAME
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
