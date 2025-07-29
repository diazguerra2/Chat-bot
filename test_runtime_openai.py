#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path
sys.path.insert(0, os.getcwd())

print("=== Runtime OpenAI Test ===")
print(f"Environment OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:10] if os.getenv('OPENAI_API_KEY') else 'NOT SET'}...")

from app.config import settings
from app.services.llm_service import llm_service

print(f"Settings OPENAI_API_KEY: {settings.OPENAI_API_KEY[:10] if settings.OPENAI_API_KEY else 'NOT SET'}...")
print(f"LLM Service api_key: {llm_service.api_key[:10] if llm_service.api_key else 'NOT SET'}...")
print(f"LLM Service OpenAI client api_key: {llm_service.openai_client.api_key[:10] if llm_service.openai_client.api_key else 'NOT SET'}...")

print("\nTesting llm_service.is_available()...")
try:
    is_available = llm_service.is_available()
    print(f"Result: {is_available}")
    
    if not is_available:
        print("\nDebugging the is_available() method...")
        print(f"- simple_openai.api_key: {llm_service.openai_client.api_key[:10] if llm_service.openai_client.api_key else 'NOT SET'}...")
        
        # Direct test
        from app.services.simple_openai import simple_openai
        print(f"- Direct simple_openai.api_key: {simple_openai.api_key[:10] if simple_openai.api_key else 'NOT SET'}...")
        print(f"- Direct simple_openai.is_available(): {simple_openai.is_available()}")
        
        # Compare instances
        print(f"- Are they the same instance? {llm_service.openai_client is simple_openai}")
        
except Exception as e:
    print(f"Exception occurred: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
