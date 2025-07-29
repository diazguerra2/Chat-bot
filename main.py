import uvicorn
import signal
import sys
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.main import app
from app.config import settings

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app):
    """Manage application lifespan"""
    # Startup
    print("[STARTUP] AI-Powered ISTQB Certification Guidance Chatbot starting...")
    yield
    # Shutdown
    print("Shutting down gracefully...")


# Add lifespan to app
app.router.lifespan_context = lifespan


def signal_handler(sig, frame):
    """Handle graceful shutdown on SIGTERM/SIGINT"""
    print(f"Received signal {sig}. Shutting down gracefully...")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check OpenAI API status
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key != 'your-openai-api-key-here':
        print(f"[OK] OpenAI API Key configured: {openai_key[:10]}...")
        # Test OpenAI connection
        try:
            from app.services.simple_openai import simple_openai
            if simple_openai.is_available():
                print(f"[OK] OpenAI API connection: ACTIVE")
            else:
                print(f"[WARNING] OpenAI API connection: FAILED")
        except Exception as e:
            print(f"[WARNING] OpenAI API test error: {e}")
    else:
        print(f"[WARNING] OpenAI API Key: NOT SET - using fallback responses")
    
    print(f"[SERVER] AI-Powered ISTQB Certification Guidance Chatbot running on port 8000")
    print(f"[INFO] Health check available at: http://localhost:8000/health")
    print(f"[INFO] Chat API available at: http://localhost:8000/api/chat")
    print(f"[INFO] Auth API available at: http://localhost:8000/api/auth")
    print(f"[INFO] Certifications API available at: http://localhost:8000/api/certifications")
    print(f"[INFO] ISTQB guidance and course recommendations ready!")
    print(f"[INFO] API documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=False,  # Temporarily disable for debugging
        log_level="info"
    )
