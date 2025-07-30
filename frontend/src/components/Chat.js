import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Upload } from 'lucide-react';
import { chatAPI } from '../services/api';
import api from '../services/api';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: '👋 Hello! I\'m your ISTQB certification guidance assistant. I can help you with:\n\n🎯 **Certification Recommendations** - Find the right cert for your experience\n📚 **Training Providers** - Connect you with quality courses\n💼 **Career Advice** - Understand the value and career impact\n📋 **Requirements & Prerequisites** - Plan your certification journey\n\nWhat would you like to know about ISTQB certifications?',
      suggestions: [
        'Which certification should I start with?',
        'Find training courses',
        'Career benefits',
        'Help me choose'
      ],
      timestamp: new Date(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (message = inputMessage) => {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(message, sessionId);
      
      if (!sessionId) {
        setSessionId(response.sessionId);
      }

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.message,
        suggestions: response.suggestions || [],
        intent: response.intent,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: '❌ Sorry, I\'m having trouble responding right now. Please try again in a moment.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || isLoading) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please select a PDF file.');
      return;
    }

    const fileSizeMB = file.size / (1024 * 1024);
    const isMassiveFile = fileSizeMB > 10; // Use enhanced processor for files > 10MB
    
    // Add user message about uploading
    const uploadMessage = {
      id: Date.now(),
      type: 'user',
      content: `📄 Uploading PDF: ${file.name} (${fileSizeMB.toFixed(1)}MB)${isMassiveFile ? ' - Using enhanced processing for large file...' : ''}`,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, uploadMessage]);

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Choose endpoint based on file size
      const endpoint = isMassiveFile ? '/chat/upload-massive-pdf' : '/chat/upload-pdf';
      
      const response = await api.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: isMassiveFile ? 300000 : 60000, // 5 min for massive files, 1 min for regular
      });

      let successContent = `✅ Successfully uploaded and processed: ${file.name}`;
      
      if (isMassiveFile && response.data.processing_stats) {
        const stats = response.data.processing_stats;
        successContent += `\n\n📊 **Processing Statistics:**\n• Pages processed: ${stats.total_pages}\n• Text chunks created: ${stats.total_chunks}\n• File size: ${stats.file_size_mb}MB\n• Method: ${stats.processing_method}`;
      }
      
      successContent += `\n\nThe PDF content has been added to my knowledge base. You can now ask me questions about the content in this document!`;

      const successMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: successContent,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, successMessage]);
    } catch (error) {
      let errorContent = `❌ Failed to upload PDF: ${file.name}`;
      
      if (error.response?.status === 413) {
        errorContent += `\n\nFile too large! Maximum size allowed is 100MB.`;
      } else if (error.code === 'ECONNABORTED') {
        errorContent += `\n\nUpload timed out. Large files may take several minutes to process.`;
      } else {
        errorContent += `\n\nError: ${error.response?.data?.detail || error.message || 'Unknown error occurred'}`;
      }
      
      errorContent += `\n\nPlease try again or contact support if the issue persists.`;

      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: errorContent,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // Clear the file input
      event.target.value = '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          ISTQB Certification Chat Assistant
        </h1>
        <p className="text-gray-600">
          Ask me anything about ISTQB certifications, training, and career guidance.
        </p>
      </div>

      {/* Chat Container */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 h-[600px] flex flex-col">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className="animate-slide-up">
              {/* Message */}
              <div className={`flex items-start space-x-3 ${
                message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-istqb-blue text-white' 
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>

                {/* Message Content */}
                <div className={`max-w-[70%] ${
                  message.type === 'user' ? 'text-right' : ''
                }`}>
                  <div className={`chat-message ${
                    message.type === 'user' ? 'chat-user' : 'chat-bot'
                  }`}>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  </div>

                  {/* Suggestions */}
                  {message.suggestions && message.suggestions.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {message.suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="suggestion-button"
                          disabled={isLoading}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Timestamp */}
                  <div className={`text-xs text-gray-500 mt-1 ${
                    message.type === 'user' ? 'text-right' : ''
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 text-gray-600 flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div className="chat-message chat-bot">
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Typing...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-3">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about ISTQB certifications..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-istqb-blue focus:border-transparent resize-none"
                rows="2"
                disabled={isLoading}
              />
            </div>
            {/* PDF Upload Button */}
            <div className="flex-shrink-0 relative">
              <input
                type="file"
                id="pdf-upload"
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
                disabled={isLoading}
              />
              <label
                htmlFor="pdf-upload"
                className={`flex items-center justify-center w-12 h-12 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-600 focus:ring-offset-2 cursor-pointer transition-colors duration-200 ${
                  isLoading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
                title="Upload PDF to knowledge base"
              >
                <Upload className="w-4 h-4" />
              </label>
            </div>
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputMessage.trim() || isLoading}
              className="flex-shrink-0 bg-istqb-blue text-white p-3 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-istqb-blue focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          {/* Quick Actions */}
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              onClick={() => handleSuggestionClick('Which certification should I start with?')}
              className="suggestion-button"
              disabled={isLoading}
            >
              Getting Started
            </button>
            <button
              onClick={() => handleSuggestionClick('I have 3 years of testing experience')}
              className="suggestion-button"
              disabled={isLoading}
            >
              Experienced Tester
            </button>
            <button
              onClick={() => handleSuggestionClick('Find training courses')}
              className="suggestion-button"
              disabled={isLoading}
            >
              Training Options
            </button>
            <button
              onClick={() => handleSuggestionClick('Career benefits of certifications')}
              className="suggestion-button"
              disabled={isLoading}
            >
              Career Impact
            </button>
          </div>
        </div>
      </div>

      {/* Tips */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 mb-2">💡 Chat Tips</h3>
        <ul className="text-sm text-blue-600 space-y-1">
          <li>• Tell me about your testing experience level</li>
          <li>• Ask about specific certifications (CTFL, CTAL-TA, etc.)</li>
          <li>• Inquire about training providers and courses</li>
          <li>• Get career advice and salary insights</li>
          <li>• <strong>📄 Upload PDF documents</strong> to expand my knowledge base with custom content</li>
        </ul>
      </div>
    </div>
  );
};

export default Chat;
