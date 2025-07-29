#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path
sys.path.insert(0, os.getcwd())

print("=== Direct LLM Service Test ===")

from app.services.llm_service import llm_service

# Test the generate_response method directly
print("Testing llm_service.generate_response with 'Who are you?'...")

try:
    response = llm_service.generate_response("Who are you?")
    print(f"Response received:")
    print(f"- Message: {response['message']}")
    print(f"- Intent: {response['intent']}")
    print(f"- Source: {response.get('source', 'not specified')}")
    print(f"- Tokens used: {response.get('tokens_used', 'not specified')}")
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
