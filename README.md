# 🎯 ISTQB Certification Guidance Chatbot

An AI-powered chatbot that helps software testing professionals choose the right ISTQB certification path, find training providers, and advance their careers.

## ✨ Features

- **🤖 AI-Powered Chat**: OpenAI GPT integration with intelligent ISTQB guidance
- **🔍 RAG System**: Retrieval-Augmented Generation with comprehensive knowledge base
- **🔐 Secure Authentication**: JWT-based user registration and login
- **📚 ISTQB Knowledge Base**: Complete certification details, requirements, and FAQs
- **🎓 Training Providers**: Comprehensive course and provider information
- **💼 Career Guidance**: Experience-based certification recommendations
- **🌐 Modern Interface**: React frontend with responsive design
- **⚡ Quick Start**: Single-command launcher for easy setup

## 🏗️ Project Structure

```
Chat-Bot/
├── app/                      # FastAPI Backend
│   ├── config.py            # Application configuration
│   ├── main.py              # FastAPI application setup
│   ├── models.py            # Data models
│   ├── data/                # ISTQB knowledge base
│   ├── middleware/          # Authentication middleware
│   ├── routes/              # API endpoints (auth, chat, certifications)
│   └── services/            # AI/LLM integration
├── frontend/                # React Frontend
│   ├── src/                 # React components and services
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration
└── start-app.py            # Single-command launcher
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** and **pip**
- **Node.js 16+** and **npm**
- **OpenAI API Key** (optional, for AI features)

### ⚡ One-Command Setup

**Windows:**
```bash
python start-app.py
# or
start-app.bat
```

**Mac/Linux:**
```bash
python3 start-app.py
# or
./start-app.sh
```

That's it! The launcher will:
- Install all dependencies automatically
- Start both backend (port 8000) and frontend (port 3000)
- Open your browser to the application

### 🔑 Login Credentials
```
Email: demo@example.com
Password: password123
```

## 🔧 Manual Setup (Optional)

If you prefer manual setup:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Configure OpenAI (optional):**
   ```bash
   # Set your OpenAI API key for AI features
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. **Start manually:**
   ```bash
   # Terminal 1 - Backend
   python main.py
   
   # Terminal 2 - Frontend  
   cd frontend && npm start
   ```

## 🤖 Using the Chatbot

The chatbot provides expert ISTQB guidance. Try these sample questions:

### 💬 Sample Conversations

**Getting Started:**
- "Which ISTQB certification should I start with?"
- "I'm new to testing, what do you recommend?"
- "Help me choose the right certification path"

**Experience-Based Advice:**
- "I have 3 years of testing experience"
- "I want to become a test manager"
- "I'm interested in automation testing"

**Certification Details:**
- "Tell me about Foundation Level certification"
- "What are the prerequisites for Advanced Level?"
- "How much does ISTQB certification cost?"

**Training & Study:**
- "Find training courses for CTFL"
- "What's the best way to study for ISTQB?"
- "How long does it take to prepare?"

## 📚 ISTQB Knowledge Base

The chatbot includes comprehensive information about:

- **Foundation Level (CTFL)**: Entry-level certification
- **Advanced Level**: Test Analyst, Test Manager, Technical Test Analyst
- **Expert Level**: Test Management, Improving the Testing Process
- **Specialist Certifications**: Agile Testing, Mobile Testing, Usability Testing
- **Training Providers**: Accredited course providers and training options
- **Career Paths**: Certification recommendations based on experience and goals

## 🔄 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Chat
- `POST /api/chat` - Send message to chatbot
- `GET /api/chat/llm-status` - Check AI integration status

### Certifications
- `GET /api/certifications` - List all ISTQB certifications
- `GET /api/certifications/{id}` - Get certification details

### System
- `GET /health` - Health check
- `GET /docs` - API documentation

## 🔒 Security & Features

- **JWT Authentication** with secure token management
- **Rate Limiting** to prevent abuse
- **Input Validation** for all API endpoints
- **CORS Protection** for cross-origin requests
- **Responsive Design** for mobile and desktop
- **Real-time Chat** with conversation history

## 🔍 RAG (Retrieval-Augmented Generation) System

The chatbot uses a sophisticated RAG system to provide accurate, contextual responses by combining:

### 📚 **Knowledge Base Components**
- **15 Comprehensive FAQs** covering all ISTQB certification levels
- **ISTQB Documentation** including testing principles, levels, and types
- **Structured Categories**: general, certifications, career, exam_info, cost, etc.
- **Keyword Indexing** for efficient content retrieval

### 🤖 **How RAG Works**
1. **Query Processing**: User question is analyzed and vectorized
2. **Content Retrieval**: Most relevant FAQ/documentation entries are found using TF-IDF similarity
3. **Context Augmentation**: Retrieved content is formatted and added to the LLM prompt
4. **Enhanced Response**: AI generates response using both general knowledge and specific ISTQB context

### 📊 **RAG API Endpoints**
- `GET /api/chat/rag-status` - Check RAG system status
- `POST /api/chat/search-knowledge` - Search knowledge base directly
- `GET /api/chat/knowledge-stats` - Get knowledge base statistics

### 📁 **Knowledge Base Structure**
```json
{
  "faq": [
    {
      "id": "istqb_intro",
      "category": "general",
      "question": "What is ISTQB?",
      "answer": "ISTQB is the International Software Testing...",
      "keywords": ["ISTQB", "certification", "testing"]
    }
  ],
  "documentation": {
    "testing_principles": {
      "title": "Seven Testing Principles",
      "content": "1. Testing shows presence of defects...",
      "keywords": ["principles", "defects", "testing"]
    }
  }
}
```

## 🧪 Testing the Application

1. **Quick Test**: Use the provided demo credentials
2. **Chat Test**: Ask about ISTQB certifications
3. **AI Test**: Check if OpenAI integration is working
4. **RAG Test**: Verify knowledge base retrieval
5. **API Test**: Use `/docs` endpoint for interactive testing

```bash
# Test the AI integration
python test_llm.py

# Test OpenAI specifically  
python test_openai.py

# Test RAG system functionality
python test_rag.py
```

## 🛠️ Troubleshooting

**Common Issues:**
- **Port conflicts**: The launcher automatically handles port conflicts
- **Dependencies**: Run `pip install -r requirements.txt` and `npm install` in frontend/
- **OpenAI errors**: Set your `OPENAI_API_KEY` environment variable
- **Browser issues**: Clear cookies for localhost

**Need Help?**
- Check the console output for detailed error messages
- Ensure all prerequisites are installed
- Try restarting the application

## 🎆 What's Next?

This chatbot provides a solid foundation for ISTQB guidance. You can extend it by:

1. **Enhanced Knowledge Base**: Add more detailed certification information
2. **Progress Tracking**: Track user certification journey
3. **Study Plans**: Generate personalized study schedules
4. **Community Features**: Connect with other testing professionals
5. **Integration**: Connect with training provider booking systems

## 📁 Project Files

**Essential Files:**
- `README.md` - Main documentation (this file)
- `OPENAI_SETUP.md` - OpenAI API setup guide
- `user-stories.md` - Product requirements and user stories
- `main.py` - Application entry point
- `start-app.py` - Single-command launcher
- `requirements.txt` - Python dependencies
- `.env` - Configuration settings

**Testing Files:**
- `test_llm.py` - Test AI integration
- `test_openai.py` - Test OpenAI API specifically
- `test_rag.py` - Test RAG system and knowledge base retrieval

**Application Structure:**
- `app/` - FastAPI backend with routes, services, and data
- `frontend/` - React frontend with components and styling

## 📄 License

This project is licensed under the ISC License.
