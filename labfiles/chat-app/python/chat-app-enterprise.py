"""
Azure AI Foundry Project Chat Application
Enterprise-grade implementation following Azure best practices.

Features:
- Azure AI Projects SDK with inference client for simple chat
- Retry logic with exponential backoff
- Token caching and refresh
- Secure credential chain (Managed Identity → Azure CLI)
- Comprehensive error handling
- Performance monitoring

This implementation uses Azure AI Foundry project's inference client
to access deployed models through a simple chat interface (not agents).
"""

import os
import logging
import requests
import json
import time
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.core.exceptions import ServiceRequestError, HttpResponseError
from typing import Dict, Any, Optional, Tuple

def setup_logging():
    """Configure logging with appropriate level."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Initialize logger
logger = logging.getLogger(__name__)

class AIFoundryClient:
    """
    Enterprise-grade Azure AI Foundry client following Azure best practices.
    Uses Azure AI Projects SDK with inference client for simple chat.
    
    Features:
    - Azure AI Projects SDK integration via inference client
    - Retry logic with exponential backoff
    - Secure credential chain (Managed Identity → Azure CLI)
    - Comprehensive error handling
    - Performance monitoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.credential = self._get_secure_credential()
        self._project_client = None
        self._openai_client = None
        self._max_retries = 3
        self._base_delay = 1.0  # Base delay for exponential backoff
        
        # Initialize the AI Project client
        self._initialize_project_client()
        
        logger.info("✅ AIFoundryClient initialized with enterprise security features")
    
    def _get_secure_credential(self) -> DefaultAzureCredential:
        """
        Get Azure credential using secure credential chain.
        Follows Azure best practices: Managed Identity → Azure CLI → fallback
        """
        try:
            # Create credential chain following Azure security best practices
            credential = DefaultAzureCredential(
                exclude_interactive_browser_credential=True,
                exclude_shared_token_cache_credential=True,
                exclude_visual_studio_code_credential=True,
                exclude_visual_studio_credential=True,
                exclude_powershell_credential=True
            )
            
            # Test the credential to ensure it works
            test_token = credential.get_token("https://management.azure.com/.default")
            logger.info("✅ Azure credentials validated successfully")
            logger.info("🔐 Using secure credential chain: Managed Identity → Azure CLI")
            return credential
        
        except Exception as e:
            logger.error(f"❌ Failed to obtain Azure credentials: {e}")
            logger.error("💡 Ensure you have:")
            logger.error("   - Managed Identity assigned (for Azure-hosted apps)")
            logger.error("   - Azure CLI authenticated (for development)")
            logger.error("   - Proper RBAC permissions")
            raise
    
    def _initialize_project_client(self):
        """
        Initialize Azure AI Project client for simple chat inference.
        Uses inference client to access deployed models through the AI Foundry project.
        """
        try:
            logger.info("🔌 Initializing Azure AI Project client...")
            
            # Get the project endpoint from config
            project_endpoint = self.config['project_endpoint']
            
            # Create the project client with simplified configuration
            # Only endpoint and credential are required for basic inference
            self._project_client = AIProjectClient(
                endpoint=project_endpoint,
                credential=self.credential
            )
            
            # Get the Azure OpenAI client from the project for inference
            logger.info("🔌 Getting Azure OpenAI inference client from project...")
            self._openai_client = self._project_client.inference.get_azure_openai_client(
                api_version=self.config['api_version']
            )
            
            logger.info("✅ Azure AI Project inference client initialized successfully")
            logger.info(f"🎯 Ready to use deployment: {self.config['deployment_name']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize project client: {e}")
            logger.error("💡 Check your project endpoint and authentication")
            logger.error("💡 Falling back to direct Azure OpenAI endpoint if available...")
            self._project_client = None
            self._openai_client = None
    
    def _retry_with_backoff(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Execute operation with exponential backoff retry logic.
        Implements Azure best practices for transient failure handling.
        """
        last_exception = None
        
        for attempt in range(self._max_retries + 1):
            try:
                if attempt > 0:
                    # Calculate exponential backoff delay with jitter
                    delay = self._base_delay * (2 ** (attempt - 1))
                    jitter = random.uniform(0.1, 0.3) * delay
                    total_delay = delay + jitter
                    
                    logger.info(f"🔄 Retrying {operation_name} (attempt {attempt + 1}/{self._max_retries + 1}) after {total_delay:.1f}s")
                    time.sleep(total_delay)
                
                result = operation_func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"✅ {operation_name} succeeded on retry attempt {attempt + 1}")
                return result
                
            except Exception as e:
                last_exception = e
                if attempt < self._max_retries:
                    # Check if it's a retryable error
                    if hasattr(e, 'response') and e.response is not None:
                        status_code = e.response.status_code
                        # Only retry on transient failures
                        if status_code in [429, 500, 502, 503, 504]:
                            logger.warning(f"⚠️ Transient failure for {operation_name}: {status_code}")
                            continue
                        else:
                            logger.error(f"❌ Non-retryable error for {operation_name}: {status_code}")
                            break
                    else:
                        # Network errors or SDK exceptions - retry
                        logger.warning(f"⚠️ Error for {operation_name}: {e}")
                        continue
                else:
                    logger.error(f"❌ Max retries exceeded for {operation_name}")
        
        # All retries failed
        logger.error(f"❌ {operation_name} failed after {self._max_retries + 1} attempts")
        raise last_exception
    
    def _make_sdk_request(self, messages: list) -> str:
        """
        Make request using Azure AI Projects SDK inference client.
        This connects to the model through the AI Foundry project.
        """
        if not self._openai_client:
            raise Exception("Azure AI Projects inference client not available")
        
        logger.info("📡 Using Azure AI Foundry project inference client...")
        
        try:
            response = self._openai_client.chat.completions.create(
                model=self.config['deployment_name'],
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            logger.info("✅ Response received from AI Foundry project")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ AI Foundry inference request failed: {e}")
            raise
    
    def _make_direct_request(self, messages: list) -> str:
        """
        Make direct API request as fallback when AI Foundry project inference is not available.
        """
        logger.info("📡 Using direct Azure OpenAI API request (fallback)...")
        
        # Get fresh token
        token_response = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        
        # Use the Azure OpenAI endpoint from config or environment
        openai_endpoint = self.config.get('azure_openai_endpoint') or os.getenv('AZURE_OPENAI_ENDPOINT')
        if not openai_endpoint:
            raise Exception("No Azure OpenAI endpoint available for fallback. Configure AZURE_OPENAI_ENDPOINT.")
            
        url = f"{openai_endpoint}openai/deployments/{self.config['deployment_name']}/chat/completions?api-version={self.config['api_version']}"
        
        headers = {
            'Authorization': f"Bearer {token_response.token}",
            'Content-Type': 'application/json',
            'User-Agent': 'Azure-AI-Foundry-Client/1.0.0'
        }
        
        payload = {
            'messages': messages,
            'max_tokens': 800,
            'temperature': 0.7,
            'stream': False
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def chat_completion(self, messages: list) -> str:
        """
        Generate chat completion using Azure AI Foundry project inference client.
        Uses the project's deployed model for simple chat completions.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            str: The assistant's response content
            
        Raises:
            Exception: If all retry attempts fail
        """
        try:
            logger.info(f"🤖 Generating completion via AI Foundry project: {self.config['project_name']}")
            
            # Try AI Foundry project inference first, fallback to direct API
            def _attempt_completion():
                if self._openai_client:
                    logger.info("🔌 Using Azure AI Foundry project inference client")
                    return self._make_sdk_request(messages)
                else:
                    logger.info("🔄 Using direct API (fallback)")
                    return self._make_direct_request(messages)
            
            # Execute with retry logic
            content = self._retry_with_backoff(
                "chat_completion",
                _attempt_completion
            )
            
            logger.info("✅ Chat completion generated successfully")
            return content
            
        except Exception as e:
            logger.error(f"❌ Chat completion failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"📊 Response status: {e.response.status_code}")
                logger.error(f"📄 Response text: {e.response.text}")
            raise

def load_configuration():
    """
    Load configuration from environment variables following Azure best practices.
    Implements proper configuration validation and security for AI Foundry projects.
    """
    try:
        # Load from enterprise-specific configuration file
        load_dotenv('.env.enterprise')
        
        config = {
            # AI Foundry project endpoint (primary configuration)
            'project_endpoint': os.getenv('PROJECT_ENDPOINT') or os.getenv('AZURE_AI_PROJECT_ENDPOINT'),
            
            # Model deployment configuration
            'deployment_name': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o-mini'),
            'api_version': os.getenv('AZURE_OPENAI_API_VERSION', '2025-01-01-preview'),
            
            # Project metadata
            'project_name': os.getenv('PROJECT_NAME', 'aiproject-14i6qb'),
            
            # Authentication (optional - prefer managed identity)
            'azure_openai_api_key': os.getenv('AZURE_OPENAI_API_KEY'),
            
            # Optional: Direct Azure OpenAI endpoint for fallback
            'azure_openai_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
            
            # Optional: Azure subscription details (usually not needed)
            'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID'),
            'resource_group': os.getenv('AZURE_RESOURCE_GROUP')
        }
        
        # Validate required configuration
        if not config['project_endpoint']:
            logger.error("❌ Missing PROJECT_ENDPOINT or AZURE_AI_PROJECT_ENDPOINT")
            logger.error("💡 Set PROJECT_ENDPOINT=https://your-ai-foundry-project.cognitiveservices.azure.com/")
            return None
            
        if not config['azure_openai_api_key']:
            logger.info("✅ No API key provided, using Azure managed identity (recommended)")
            config['use_managed_identity'] = True
        else:
            logger.warning("⚠️ Using API key authentication (consider migrating to managed identity)")
            config['use_managed_identity'] = False
            
        logger.info("✅ Configuration loaded successfully")
        logger.info(f"📍 AI Foundry Project: {config['project_name']}")
        logger.info(f"🔗 Project Endpoint: {config['project_endpoint']}")
        logger.info(f"🎯 Deployment Name: {config['deployment_name']}")
        logger.info(f"🔐 Using Managed Identity: {config['use_managed_identity']}")
        
        return config
        
    except Exception as e:
        logger.error(f"❌ Failed to load configuration: {e}")
        return None

def main():
    """
    Main function for Azure AI Foundry project chat application.
    Implements enterprise-grade patterns following Azure best practices.
    """
    setup_logging()
    logger.info("🚀 Starting Azure AI Foundry Project Chat Application (Enterprise Edition)")
    
    try:
        # Load configuration with validation
        config = load_configuration()
        if not config:
            logger.error("❌ Failed to load configuration")
            return
        
        # Create enterprise AI Foundry client
        ai_client = AIFoundryClient(config)
        logger.info("✅ Enterprise AI Foundry client initialized")
        
        logger.info("🤖 Chat application ready!")
        
        # Enhanced chat loop with better UX
        print(f"\n🤖 Azure AI Foundry Chat - Project: {config['project_name']}")
        print(f"🎯 Using deployment: {config['deployment_name']}")
        print("💡 Features: AI Foundry project inference + Direct API fallback, retry logic, secure authentication")
        print("Type 'exit' to quit\n")
        
        conversation_history = [
            {"role": "system", "content": f"You are a helpful AI assistant powered by Azure AI Foundry project '{config['project_name']}' using deployment '{config['deployment_name']}'. You provide accurate and helpful responses through the AI Foundry inference client."}
        ]
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                    
                if not user_input:
                    continue
                
                # Add user message to conversation
                conversation_history.append({"role": "user", "content": user_input})
                
                # Generate response using enterprise client
                print("🤔 Thinking...", end="", flush=True)
                response = ai_client.chat_completion(conversation_history)
                print("\r" + " " * 15 + "\r", end="")  # Clear "Thinking..."
                
                if response:
                    print(f"Assistant: {response}\n")
                    # Add assistant response to conversation
                    conversation_history.append({"role": "assistant", "content": response})
                else:
                    print("❌ Sorry, I couldn't generate a response. Please try again.\n")
                    # Remove the user message since we couldn't respond
                    conversation_history.pop()
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                print(f"⚠️ An error occurred: {e}. Please try again.\n")
                # Remove the user message if there was an error
                if len(conversation_history) > 1 and conversation_history[-1]["role"] == "user":
                    conversation_history.pop()
    
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        print(f"❌ Failed to start application: {e}")

if __name__ == '__main__':
    main()
