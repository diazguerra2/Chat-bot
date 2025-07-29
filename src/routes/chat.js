const express = require('express');
const { body, validationResult } = require('express-validator');
const authMiddleware = require('../middleware/auth');
const router = express.Router();

// Chat rate limiting (more restrictive than global)
const chatRateLimit = require('express-rate-limit')({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 10, // limit each IP to 10 chat requests per minute
    message: 'Too many chat requests, please wait before sending another message.'
});

// Apply auth middleware to all chat routes
router.use(authMiddleware);
router.use(chatRateLimit);

// Validation middleware
const validateChatMessage = [
    body('message')
        .trim()
        .isLength({ min: 1, max: 1000 })
        .withMessage('Message must be between 1 and 1000 characters'),
    body('sessionId')
        .optional()
        .isUUID()
        .withMessage('Session ID must be a valid UUID')
];

/**
 * @route POST /api/chat
 * @desc Send message to chatbot and get response
 * @access Private
 */
router.post('/', validateChatMessage, async (req, res) => {
    try {
        // Check for validation errors
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({
                error: 'Validation failed',
                details: errors.array()
            });
        }

        const { message, sessionId } = req.body;
        const userId = req.user.userId;

        // Generate session ID if not provided
        const currentSessionId = sessionId || require('crypto').randomUUID();

        // Log the conversation (in production, store in database)
        console.log(`Chat - User ${userId}: ${message}`);

        // Basic chatbot logic (will be enhanced with LLM integration)
        const botResponse = await generateChatbotResponse(message, userId);

        // Store conversation history (implement in database later)
        const conversationEntry = {
            sessionId: currentSessionId,
            userId,
            userMessage: message,
            botResponse: botResponse.message,
            timestamp: new Date().toISOString(),
            intent: botResponse.intent
        };

        res.json({
            sessionId: currentSessionId,
            message: botResponse.message,
            intent: botResponse.intent,
            suggestions: botResponse.suggestions || [],
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        console.error('Chat error:', error);
        res.status(500).json({
            error: 'Chat service unavailable',
            message: 'Sorry, I\'m having trouble responding right now. Please try again later.'
        });
    }
});

/**
 * @route GET /api/chat/history
 * @desc Get chat history for the user
 * @access Private
 */
router.get('/history', (req, res) => {
    // This would fetch from database in production
    res.json({
        message: 'Chat history endpoint - to be implemented with database',
        userId: req.user.userId
    });
});

/**
 * Basic chatbot response generation
 * This will be replaced with LLM integration in Part 4
 */
async function generateChatbotResponse(message, userId) {
    const lowerMessage = message.toLowerCase().trim();

    // Order status patterns
    if (lowerMessage.includes('order') && (lowerMessage.includes('status') || lowerMessage.includes('#'))) {
        return {
            intent: 'order_status',
            message: '🔍 I can help you check your order status! Could you please provide your order number? It usually starts with # followed by numbers.',
            suggestions: ['Check order #12345', 'My recent orders', 'Help with orders']
        };
    }

    // Order details patterns
    if (lowerMessage.includes('order') && lowerMessage.includes('details')) {
        return {
            intent: 'order_details',
            message: '📋 I can show you detailed information about your order. Please share your order number so I can look it up for you.',
            suggestions: ['Order #12345 details', 'What did I order?', 'Order summary']
        };
    }

    // Shipping patterns
    if (lowerMessage.includes('shipping') || lowerMessage.includes('delivery') || lowerMessage.includes('track')) {
        return {
            intent: 'shipping_info',
            message: '🚚 I can help you with shipping and delivery information! Please provide your order number to get tracking details.',
            suggestions: ['Track order #12345', 'Delivery time', 'Shipping options']
        };
    }

    // Return patterns
    if (lowerMessage.includes('return') || lowerMessage.includes('refund')) {
        return {
            intent: 'return_request',
            message: '↩️ I can help you with returns and refunds. Our return policy allows returns within 30 days. What would you like to return?',
            suggestions: ['Return policy', 'Start a return', 'Refund status']
        };
    }

    // Greeting patterns
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
        return {
            intent: 'greeting',
            message: '👋 Hello! I\'m your order assistant. I can help you with order status, shipping information, returns, and more. How can I assist you today?',
            suggestions: ['Check order status', 'Track my package', 'Return an item', 'Help']
        };
    }

    // Help patterns
    if (lowerMessage.includes('help') || lowerMessage.includes('what can you do')) {
        return {
            intent: 'help',
            message: '🤖 I\'m here to help with your orders! I can:\n\n• Check order status and details\n• Provide shipping and tracking information\n• Help with returns and refunds\n• Answer questions about our policies\n\nJust ask me about any of these topics!',
            suggestions: ['Check order status', 'Shipping info', 'Return policy', 'Track package']
        };
    }

    // Default response
    return {
        intent: 'unknown',
        message: '🤔 I\'m not sure I understand. I specialize in helping with orders, shipping, and returns. Could you please rephrase your question or ask me about:\n\n• Order status\n• Tracking information\n• Returns and refunds\n• General help',
        suggestions: ['Check order status', 'Help', 'What can you do?', 'Track my order']
    };
}

module.exports = router;
