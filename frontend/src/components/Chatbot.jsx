import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';

/**
 * Chatbot Component
 * AI-powered assistant using GPT-5 for intelligent conversations
 * 
 * Features:
 * - Floating chat button in bottom-right
 * - Collapsible chat interface
 * - Message history
 * - Typing indicator
 * - Auto-scroll to latest message
 */
function Chatbot() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([{
        id: 1,
        text: "Hi! I'm your Perceptron AI assistant powered by GPT-5. How can I help you analyze your intelligence data today?",
        sender: 'bot',
        timestamp: new Date()
    }]);
    const [inputText, setInputText] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    // Focus input when chat opens
    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

    const scrollToBottom = () => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const toggleChat = () => {
        setIsOpen(!isOpen);
    };

    const handleSendMessage = async(e) => {
        e.preventDefault();

        if (!inputText.trim()) return;

        // Add user message
        const userMessage = {
            id: Date.now(),
            text: inputText,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputText('');
        setIsTyping(true);

        // Simulate GPT-5 API call
        try {
            // TODO: Replace with actual GPT-5 API call
            await new Promise(resolve => setTimeout(resolve, 1500));

            const botResponse = {
                id: Date.now() + 1,
                text: generateResponse(inputText),
                sender: 'bot',
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botResponse]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                id: Date.now() + 1,
                text: "I apologize, but I'm having trouble connecting. Please try again.",
                sender: 'bot',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsTyping(false);
        }
    };

    // Placeholder response generator (replace with actual GPT-5 API)
    const generateResponse = (userInput) => {
        const lowerInput = userInput.toLowerCase();

        if (lowerInput.includes('keyword') || lowerInput.includes('trend')) {
            return "I can help you analyze keyword trends! Based on your current data, I see several emerging patterns. Would you like me to generate a detailed report or visualize specific metrics?";
        } else if (lowerInput.includes('report') || lowerInput.includes('export')) {
            return "I can help you generate and export reports in multiple formats (PDF, Excel, CSV). What date range and metrics would you like to include?";
        } else if (lowerInput.includes('team')) {
            return "You have access to multiple team perspectives: Competitor, Investor, Regulator, and Researcher. Which team's data would you like to explore?";
        } else if (lowerInput.includes('help')) {
            return "I can assist you with:\n• Analyzing keyword trends and patterns\n• Generating custom reports\n• Explaining data insights\n• Setting up alerts\n• Filtering and searching data\n\nWhat would you like to know more about?";
        } else {
            return "That's an interesting question! As your AI assistant, I can help you analyze intelligence data, generate insights, and navigate the Perceptron platform. Could you provide more details about what you'd like to accomplish?";
        }
    };

    const formatTimestamp = (date) => {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="chatbot-container">
            {/* Chat Window */}
            {isOpen && (
                <div className="chatbot-window">
                    {/* Header */}
                    <div className="chatbot-header">
                        <div className="chatbot-header-info">
                            <div className="chatbot-avatar">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" />
                                </svg>
                            </div>
                            <div className="chatbot-header-text">
                                <h3>Perceptron AI</h3>
                                <span className="chatbot-status">
                                    <span className="status-dot"></span>
                                    Online
                                </span>
                            </div>
                        </div>
                        <button
                            className="chatbot-close"
                            onClick={toggleChat}
                            aria-label="Close chat"
                        >
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M10 8.586L2.929 1.515 1.515 2.929 8.586 10l-7.071 7.071 1.414 1.414L10 11.414l7.071 7.071 1.414-1.414L11.414 10l7.071-7.071-1.414-1.414L10 8.586z" />
                            </svg>
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="chatbot-messages">
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`chatbot-message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
                            >
                                <div className="message-content">
                                    <p>{message.text}</p>
                                    <span className="message-timestamp">{formatTimestamp(message.timestamp)}</span>
                                </div>
                            </div>
                        ))}

                        {/* Typing Indicator */}
                        {isTyping && (
                            <div className="chatbot-message bot-message">
                                <div className="message-content typing-indicator">
                                    <div className="typing-dot"></div>
                                    <div className="typing-dot"></div>
                                    <div className="typing-dot"></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <form className="chatbot-input-container" onSubmit={handleSendMessage}>
                        <input
                            ref={inputRef}
                            type="text"
                            className="chatbot-input"
                            placeholder="Ask me anything about your data..."
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            aria-label="Chat message input"
                        />
                        <button
                            type="submit"
                            className="chatbot-send-btn"
                            disabled={!inputText.trim() || isTyping}
                            aria-label="Send message"
                        >
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                            </svg>
                        </button>
                    </form>
                </div>
            )}

            {/* Floating Button */}
            <button
                className={`chatbot-toggle ${isOpen ? 'active' : ''}`}
                onClick={toggleChat}
                aria-label={isOpen ? 'Close chat' : 'Open chat'}
            >
                {isOpen ? (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                    </svg>
                ) : (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" />
                    </svg>
                )}
            </button>
        </div>
    );
}

export default Chatbot;