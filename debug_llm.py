#!/usr/bin/env python3

import sys
import os
import traceback

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    from app.services.llm_service import llm_service
    from app.services.simple_openai import simple_openai
    
    print("=== LLM Service Debug ===")
    print(f"OpenAI API Key set: {bool(simple_openai.api_key and simple_openai.api_key != 'your-openai-api-key-here')}")
    print(f"OpenAI available: {simple_openai.is_available()}")
    print(f"LLM service available: {llm_service.is_available()}")
    
    # Test the exact call that would be made from the chat endpoint
    print("\n=== Testing generate_response ===")
    response = llm_service.generate_response(
        message="who are you?",
        context="User ID: demo2, Session: test-session"
    )
    
    print(f"Response keys: {list(response.keys())}")
    print(f"Response source: {response.get('source', 'NOT SET')}")
    print(f"Response message length: {len(response.get('message', ''))}")
    print(f"Response tokens used: {response.get('tokens_used', 'NOT SET')}")
    print(f"RAG context used: {response.get('rag_context_used', 'NOT SET')}")
    print(f"Message preview: {response.get('message', '')[:200]}...")
    
except Exception as e:
    print(f"Error occurred: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
