from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from app.routes import auth, chat, certifications, advice
from app.config import settings
from datetime import datetime
from contextlib import asynccontextmanager
import time
import os

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Add state for tracking startup time
startup_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    # Startup
    print("[STARTUP] AI-Powered ISTQB Certification Guidance Chatbot starting...")
    
    # Check OpenAI API status
    openai_key = settings.OPENAI_API_KEY
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
    
    yield
    
    # Shutdown
    print("[SHUTDOWN] Shutting down gracefully...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="AI-Powered ISTQB Certification Guidance Chatbot",
    description="Intelligent guidance system for ISTQB testing certifications",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up rate limiting
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Add routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(certifications.router, prefix="/api/certifications", tags=["certifications"])
app.include_router(advice.router, prefix="/api/advice", tags=["advice"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Powered ISTQB Certification Guidance Chatbot",
        "version": "1.0.0",
        "description": "Intelligent guidance system for ISTQB testing certifications",
        "features": [
            "Personalized certification recommendations",
            "Training provider referrals",
            "Experience-based career advice",
            "Course and exam information"
        ],
        "endpoints": {
            "authentication": "/api/auth",
            "chat": "/api/chat",
            "certifications": "/api/certifications",
            "health": "/health"
        },
        "documentation": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - startup_time
    })


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    print(f"Error: {request.method} {request.url} caused {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "Something went wrong"},
    )

