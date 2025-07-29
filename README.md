# AI-Powered Chatbot Order Status Service

A comprehensive e-commerce chatbot service built with Node.js and Express that helps customers with order inquiries, status checks, shipping information, and returns processing.

## 🚀 Features

### Core Functionality
- **JWT Authentication**: Secure user registration and login system
- **AI Chatbot**: Intelligent order assistance with natural language processing
- **Order Management**: Complete order status, details, and modification tracking
- **Shipping Integration**: Real-time tracking and delivery information
- **Security**: Rate limiting, input validation, and secure middleware
- **RESTful API**: Well-structured endpoints following REST principles

### Chatbot Capabilities
- Order status inquiries
- Detailed order information retrieval
- Shipping and tracking information
- Return and refund assistance
- Order modification requests
- Natural language understanding

## 📋 Project Structure

```
ai-chatbot-order-service/
├── src/
│   ├── app.js                 # Main Express application
│   ├── controllers/           # Request handlers (future)
│   ├── middleware/
│   │   └── auth.js           # JWT authentication middleware
│   ├── models/               # Data models (future)
│   ├── routes/
│   │   ├── auth.js           # Authentication routes
│   │   ├── chat.js           # Chatbot interaction routes
│   │   └── orders.js         # Order management routes
│   ├── services/             # Business logic (future)
│   └── utils/                # Utility functions (future)
├── config/                   # Configuration files (future)
├── data/                     # Mock data and knowledge base
├── server.js                 # Server entry point
├── user-stories.md           # Product requirements and user stories
├── .env                      # Environment configuration
├── package.json              # Node.js project configuration
└── README.md                 # Project documentation
```

## 🛠️ Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn package manager

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd Chat-Bot
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   - Copy `.env` and update the values:
   ```bash
   # Update JWT_SECRET and other configuration values
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   Or for production:
   ```bash
   npm start
   ```

5. **Verify the installation:**
   - Health check: `GET http://localhost:3000/health`
   - API documentation: `GET http://localhost:3000/`

## 🔧 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

### Chat Endpoints

#### Send Message to Chatbot
```http
POST /api/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "What's the status of my order #12345?",
  "sessionId": "optional-session-uuid"
}
```

### Order Endpoints

#### Get Order Details
```http
GET /api/orders/12345
Authorization: Bearer <jwt_token>
```

#### Check Order Status
```http
GET /api/orders/12345/status
Authorization: Bearer <jwt_token>
```

#### Get Shipping Information
```http
GET /api/orders/12345/shipping
Authorization: Bearer <jwt_token>
```

## 🤖 Using the Chatbot

The chatbot understands natural language queries related to:

### Example Interactions

**Order Status:**
- "What's the status of order #12345?"
- "Check my order 67890"
- "Where is my package?"

**Order Details:**
- "Show me details for order #12345"
- "What did I order?"
- "Order summary for #67890"

**Shipping & Tracking:**
- "When will my order arrive?"
- "Track order #12345"
- "Delivery information"

**Returns & Refunds:**
- "How do I return this item?"
- "Refund policy"
- "Start a return for order #12345"

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Protection against abuse and DDoS
- **Input Validation**: Comprehensive request validation
- **Security Headers**: Helmet.js for security headers
- **CORS Configuration**: Controlled cross-origin access
- **Password Hashing**: bcrypt for secure password storage

## 🚧 Development Status

### Completed (Parts 1-3)
- ✅ User stories and MVP definition
- ✅ Project scaffolding and structure
- ✅ Authentication system with JWT
- ✅ Protected chat endpoints
- ✅ Basic chatbot logic
- ✅ Order management API

### In Progress
- 🔄 LLM integration (Part 4)
- 🔄 RAG knowledge base (Part 5)
- 🔄 Database integration
- 🔄 Advanced NLP processing

### Planned
- 📋 Comprehensive testing suite
- 📋 API documentation with Swagger
- 📋 Docker containerization
- 📋 Production deployment guides
- 📋 Performance monitoring

## 🧪 Testing

### Manual Testing

1. **Test Authentication:**
   ```bash
   # Register a new user
   curl -X POST http://localhost:3000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
   
   # Login
   curl -X POST http://localhost:3000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

2. **Test Chat (with token):**
   ```bash
   curl -X POST http://localhost:3000/api/chat \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"message":"Hello, what can you help me with?"}'
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.

## ✨ Acknowledgments

- Built as part of an AI-powered chatbot development challenge
- Focuses on e-commerce order management use cases
- Designed for scalability and enterprise integration
