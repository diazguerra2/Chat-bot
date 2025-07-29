#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== OpenAI API Debug Test ===")
print(f"Environment OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:10] if os.getenv('OPENAI_API_KEY') else 'NOT SET'}...")

# Add the current directory to the path
sys.path.insert(0, os.getcwd())

from app.config import settings
from app.services.simple_openai import simple_openai

print(f"Settings OPENAI_API_KEY: {settings.OPENAI_API_KEY[:10] if settings.OPENAI_API_KEY else 'NOT SET'}...")
print(f"SimpleOpenAI api_key: {simple_openai.api_key[:10] if simple_openai.api_key else 'NOT SET'}...")

print("\nTesting simple_openai.is_available()...")
try:
    is_available = simple_openai.is_available()
    print(f"Result: {is_available}")
    
    if not is_available:
        print("\nDebugging the is_available() method...")
        import requests
        
        if not simple_openai.api_key:
            print("- API key is missing or empty")
        else:
            print(f"- API key is present: {simple_openai.api_key[:10]}...")
            
            headers = {
                "Authorization": f"Bearer {simple_openai.api_key}",
                "Content-Type": "application/json"
            }
            
            print("- Making request to https://api.openai.com/v1/models")
            try:
                response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
                print(f"- Response status code: {response.status_code}")
                print(f"- Response headers: {dict(response.headers)}")
                if response.status_code != 200:
                    print(f"- Response text: {response.text}")
            except Exception as e:
                print(f"- Request failed with exception: {e}")
            
except Exception as e:
    print(f"Exception occurred: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
