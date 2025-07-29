# 🔑 OpenAI API Setup Guide

This guide helps you enable AI-powered responses in the ISTQB chatbot using OpenAI's API.

## 🚀 Quick Setup

### 1. Get an OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy your API key (starts with `sk-proj-...`)

### 2. Set the API Key

**Windows:**
```bash
set OPENAI_API_KEY=your-api-key-here
python start-app.py
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY="your-api-key-here"
python3 start-app.py
```

**Or edit your `.env` file:**
```env
OPENAI_API_KEY=your-api-key-here
```

### 3. Verify Setup

```bash
# Test the integration
python test_openai.py

# Or check the API status in the app
# Visit: http://localhost:8000/api/chat/llm-status
```

## 💰 Pricing

- **GPT-3.5-turbo**: ~$0.002 per 1K tokens (very affordable)
- **GPT-4**: ~$0.03 per 1K tokens (more expensive but better quality)
- **Free tier**: $5 of free credits for new accounts

**Estimate**: 1000 chat messages ≈ $2-5 with GPT-3.5-turbo

## 🛡️ Without OpenAI API

The chatbot works without OpenAI API by using rule-based responses:
- Still provides accurate ISTQB guidance
- Uses predefined knowledge base
- No API costs
- Responses are more structured but less conversational

## 🔧 Configuration

The system uses **GPT-3.5-turbo** by default for cost efficiency. To change models, edit `app/services/llm_service.py`:

```python
self.model_name = "gpt-4"  # For better quality
# or
self.model_name = "gpt-3.5-turbo"  # For lower cost
```

## ✅ Benefits of AI Integration

- **Natural Conversations**: More human-like responses
- **Context Understanding**: Better interpretation of user questions
- **Personalized Advice**: Tailored recommendations based on user input
- **Follow-up Questions**: Smart conversation flow
- **Complex Queries**: Handles nuanced testing scenarios

The chatbot provides excellent ISTQB guidance both with and without AI integration!
