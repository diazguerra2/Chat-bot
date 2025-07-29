import os
import requests
import json
from typing import Dict, Any
from app.config import settings

class SimpleOpenAIService:
    """Simple OpenAI service using direct HTTP requests"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        if not self.api_key:
            return False
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def chat_completion(self, messages: list, temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        """Make a chat completion request"""
        if not self.api_key:
            raise Exception("OpenAI API key not set")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

# Global instance
simple_openai = SimpleOpenAIService()
