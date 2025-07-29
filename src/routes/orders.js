const express = require('express');
const authMiddleware = require('../middleware/auth');
const router = express.Router();

// Apply auth middleware to all order routes
router.use(authMiddleware);

// Mock order data (replace with database in production)
const mockOrders = new Map([
    ['12345', {
        id: '12345',
        userId: '1',
        status: 'shipped',
        items: [
            { name: 'Wireless Headphones', quantity: 1, price: 99.99 },
            { name: 'Phone Case', quantity: 2, price: 15.99 }
        ],
        total: 131.97,
        shippingAddress: {
            street: '123 Main St',
            city: 'Anytown',
            state: 'CA',
            zip: '12345'
        },
        trackingNumber: 'TRK123456789',
        estimatedDelivery: '2024-01-15',
        createdAt: '2024-01-10T10:00:00Z'
    }],
    ['67890', {
        id: '67890',
        userId: '1',
        status: 'processing',
        items: [
            { name: 'Laptop Stand', quantity: 1, price: 49.99 }
        ],
        total: 49.99,
        shippingAddress: {
            street: '123 Main St',
            city: 'Anytown',
            state: 'CA',
            zip: '12345'
        },
        trackingNumber: null,
        estimatedDelivery: '2024-01-20',
        createdAt: '2024-01-12T14:30:00Z'
    }]
]);

/**
 * @route GET /api/orders/:orderId
 * @desc Get order details by ID
 * @access Private
 */
router.get('/:orderId', (req, res) => {
    try {
        const { orderId } = req.params;
        const userId = req.user.userId;

        const order = mockOrders.get(orderId);
        
        if (!order) {
            return res.status(404).json({
                error: 'Order not found',
                message: `Order ${orderId} does not exist`
            });
        }

        // Check if user owns this order
        if (order.userId !== userId) {
            return res.status(403).json({
                error: 'Access denied',
                message: 'You can only access your own orders'
            });
        }

        res.json({
            order: {
                ...order,
                // Mask sensitive information
                shippingAddress: {
                    ...order.shippingAddress,
                    street: order.shippingAddress.street.replace(/\d+/, '***')
                }
            }
        });

    } catch (error) {
        console.error('Get order error:', error);
        res.status(500).json({
            error: 'Unable to retrieve order',
            message: 'An error occurred while fetching order details'
        });
    }
});

/**
 * @route GET /api/orders/:orderId/status
 * @desc Get order status by ID
 * @access Private
 */
router.get('/:orderId/status', (req, res) => {
    try {
        const { orderId } = req.params;
        const userId = req.user.userId;

        const order = mockOrders.get(orderId);
        
        if (!order) {
            return res.status(404).json({
                error: 'Order not found',
                message: `Order ${orderId} does not exist`
            });
        }

        // Check if user owns this order
        if (order.userId !== userId) {
            return res.status(403).json({
                error: 'Access denied',
                message: 'You can only access your own orders'
            });
        }

        res.json({
            orderId: order.id,
            status: order.status,
            estimatedDelivery: order.estimatedDelivery,
            trackingNumber: order.trackingNumber,
            lastUpdated: new Date().toISOString()
        });

    } catch (error) {
        console.error('Get order status error:', error);
        res.status(500).json({
            error: 'Unable to retrieve order status',
            message: 'An error occurred while fetching order status'
        });
    }
});

/**
 * @route GET /api/orders/:orderId/shipping
 * @desc Get shipping information for an order
 * @access Private
 */
router.get('/:orderId/shipping', (req, res) => {
    try {
        const { orderId } = req.params;
        const userId = req.user.userId;

        const order = mockOrders.get(orderId);
        
        if (!order) {
            return res.status(404).json({
                error: 'Order not found',
                message: `Order ${orderId} does not exist`
            });
        }

        // Check if user owns this order
        if (order.userId !== userId) {
            return res.status(403).json({
                error: 'Access denied',
                message: 'You can only access your own orders'
            });
        }

        res.json({
            orderId: order.id,
            trackingNumber: order.trackingNumber,
            carrier: order.trackingNumber ? 'FedEx' : null,
            status: order.status,
            estimatedDelivery: order.estimatedDelivery,
            shippingAddress: order.shippingAddress
        });

    } catch (error) {
        console.error('Get shipping info error:', error);
        res.status(500).json({
            error: 'Unable to retrieve shipping information',
            message: 'An error occurred while fetching shipping details'
        });
    }
});

/**
 * @route GET /api/orders/:orderId/modifiable
 * @desc Check if order can be modified
 * @access Private
 */
router.get('/:orderId/modifiable', (req, res) => {
    try {
        const { orderId } = req.params;
        const userId = req.user.userId;

        const order = mockOrders.get(orderId);
        
        if (!order) {
            return res.status(404).json({
                error: 'Order not found',
                message: `Order ${orderId} does not exist`
            });
        }

        // Check if user owns this order
        if (order.userId !== userId) {
            return res.status(403).json({
                error: 'Access denied',
                message: 'You can only access your own orders'
            });
        }

        const canModify = order.status === 'pending' || order.status === 'processing';

        res.json({
            orderId: order.id,
            canModify,
            reason: canModify ? 'Order can be modified' : 'Order has already shipped and cannot be modified',
            currentStatus: order.status
        });

    } catch (error) {
        console.error('Check modifiable error:', error);
        res.status(500).json({
            error: 'Unable to check modification status',
            message: 'An error occurred while checking if order can be modified'
        });
    }
});

/**
 * @route PUT /api/orders/:orderId
 * @desc Modify an order (if possible)
 * @access Private
 */
router.put('/:orderId', (req, res) => {
    try {
        const { orderId } = req.params;
        const userId = req.user.userId;

        const order = mockOrders.get(orderId);
        
        if (!order) {
            return res.status(404).json({
                error: 'Order not found',
                message: `Order ${orderId} does not exist`
            });
        }

        // Check if user owns this order
        if (order.userId !== userId) {
            return res.status(403).json({
                error: 'Access denied',
                message: 'You can only modify your own orders'
            });
        }

        const canModify = order.status === 'pending' || order.status === 'processing';
        
        if (!canModify) {
            return res.status(400).json({
                error: 'Cannot modify order',
                message: 'This order has already shipped and cannot be modified'
            });
        }

        res.json({
            message: 'Order modification endpoint - to be implemented',
            orderId: order.id,
            note: 'In a full implementation, this would handle order modifications'
        });

    } catch (error) {
        console.error('Modify order error:', error);
        res.status(500).json({
            error: 'Unable to modify order',
            message: 'An error occurred while modifying the order'
        });
    }
});

module.exports = router;
