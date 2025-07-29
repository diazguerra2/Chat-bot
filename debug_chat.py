#!/usr/bin/env python3

import requests
import json

# Test the chat endpoint directly
def test_chat_endpoint():
    # First, login to get a token
    login_data = {
        "email": "demo@example.com",
        "password": "demo"
    }
    
    login_response = requests.post("http://localhost:8001/api/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        return
    
    response_data = login_response.json()
    print(f"Login response: {response_data}")
    token = response_data["token"]
    print(f"Login successful, token: {token[:20]}...")
    
    # Now test the chat endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    chat_data = {
        "message": "who are you?",
        "sessionId": None
    }
    
    print(f"Sending chat request to http://localhost:8001/api/chat/")
    chat_response = requests.post("http://localhost:8001/api/chat/", json=chat_data, headers=headers)
    
    print(f"Chat response status: {chat_response.status_code}")
    print(f"Chat response headers: {dict(chat_response.headers)}")
    
    if chat_response.status_code == 200:
        response_data = chat_response.json()
        print(f"Response source: {response_data.get('source', 'not specified')}")
        print(f"Message length: {len(response_data.get('message', ''))}")
        print(f"Message preview: {response_data.get('message', '')[:200]}...")
        print(f"Tokens used: {response_data.get('tokens_used', 'N/A')}")
    else:
        print(f"Chat failed: {chat_response.text}")

if __name__ == "__main__":
    test_chat_endpoint()
