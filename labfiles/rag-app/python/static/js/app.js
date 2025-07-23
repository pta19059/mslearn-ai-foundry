// Margie's Travel RAG App - Interactive JavaScript
class ChatApp {
    constructor() {
        this.isLoading = false;
        this.messageHistory = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
        this.setupSuggestions();
        console.log('🤖 Margie\'s Travel Assistant initialized');
    }

    bindEvents() {
        // Form submission
        const chatForm = document.getElementById('chatForm');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const clearButton = document.getElementById('clearChat');

        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSendMessage();
            });
        }

        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });

            // Auto-resize input
            messageInput.addEventListener('input', () => {
                this.updateSendButton();
            });
        }

        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearChat();
            });
        }

        // Window resize handling
        window.addEventListener('resize', () => {
            this.scrollToBottom();
        });
    }

    setupSuggestions() {
        // Bind suggestion clicks
        document.querySelectorAll('.suggestion-badge').forEach(badge => {
            badge.addEventListener('click', () => {
                const suggestion = badge.getAttribute('data-suggestion');
                if (suggestion) {
                    document.getElementById('messageInput').value = suggestion;
                    document.getElementById('messageInput').focus();
                    this.updateSendButton();
                }
            });
        });
    }

    updateSendButton() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        
        if (messageInput && sendButton) {
            const hasText = messageInput.value.trim().length > 0;
            sendButton.disabled = !hasText || this.isLoading;
            
            if (hasText && !this.isLoading) {
                sendButton.classList.add('btn-primary');
                sendButton.classList.remove('btn-secondary');
            } else {
                sendButton.classList.add('btn-secondary');
                sendButton.classList.remove('btn-primary');
            }
        }
    }

    async handleSendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message || this.isLoading) return;

        this.isLoading = true;
        this.updateSendButton();

        // Hide welcome message
        this.hideWelcomeMessage();

        // Add user message
        this.addMessage(message, 'user');
        messageInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await this.sendMessageToAPI(message);
            this.hideTypingIndicator();
            
            if (response.response) {
                this.addMessage(response.response, 'assistant');
            } else {
                throw new Error('No response received');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.handleError(error);
        } finally {
            this.isLoading = false;
            this.updateSendButton();
            messageInput.focus();
        }
    }

    async sendMessageToAPI(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        return await response.json();
    }

    addMessage(content, role) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        // Format content (basic markdown support)
        const formattedContent = this.formatMessage(content);
        bubbleDiv.innerHTML = formattedContent;

        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        metaDiv.textContent = this.getCurrentTime();

        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(metaDiv);
        chatMessages.appendChild(messageDiv);

        // Store in history
        this.messageHistory.push({ content, role, timestamp: new Date() });

        this.scrollToBottom();
    }

    formatMessage(content) {
        // Basic markdown formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            // Add travel-specific formatting
            .replace(/(\$\d+(?:\.\d{2})?)/g, '<span class="text-success fw-bold">$1</span>')
            .replace(/(★+)/g, '<span class="text-warning">$1</span>');
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <i class="fas fa-robot me-2 text-primary"></i>
            <span>Assistant is typing</span>
            <div class="typing-dots ms-2">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    hideWelcomeMessage() {
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
    }

    showWelcomeMessage() {
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'block';
        }
    }

    handleError(error) {
        console.error('Chat error:', error);
        
        const chatMessages = document.getElementById('chatMessages');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            <span>Sorry, I encountered an error: ${error.message}</span>
            <button class="retry-btn ms-auto" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }

        try {
            const response = await fetch('/api/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Clear UI
                const chatMessages = document.getElementById('chatMessages');
                chatMessages.innerHTML = '';
                
                // Reset state
                this.messageHistory = [];
                
                // Show welcome message
                this.showWelcomeMessage();
                
                // Show success feedback
                this.showNotification('Chat history cleared!', 'success');
                
                console.log('💫 Chat cleared successfully');
            } else {
                throw new Error('Failed to clear chat');
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
            this.showNotification('Failed to clear chat', 'error');
        }
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/api/history');
            if (response.ok) {
                const data = await response.json();
                
                if (data.messages && data.messages.length > 0) {
                    this.hideWelcomeMessage();
                    
                    data.messages.forEach(msg => {
                        this.addMessage(msg.content, msg.role);
                    });
                    
                    console.log(`📜 Loaded ${data.messages.length} messages`);
                }
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
    
    // Add some helpful console messages
    console.log(`
    🌍 Welcome to Margie's Travel Assistant!
    
    This AI-powered travel assistant can help you with:
    • Destination information
    • Hotel recommendations  
    • Travel planning
    • Booking assistance
    
    Try asking about popular destinations like Dubai, London, New York, Las Vegas, or San Francisco!
    `);
});

// Add global error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

// Add service worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
