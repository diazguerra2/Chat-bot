#!/usr/bin/env python3
"""
Test script for OpenAI LLM integration with ISTQB Chatbot
This script tests the OpenAI GPT integration functionality
"""

import os
import sys
sys.path.append('.')

from app.services.llm_service import llm_service

def test_openai_integration():
    print("🧪 Testing OpenAI LLM Integration for ISTQB Chatbot")
    print("=" * 55)
    
    # Check OpenAI status
    print("🔍 Checking OpenAI API status...")
    is_available = llm_service.is_available()
    api_key_configured = bool(llm_service.api_key)
    models = llm_service.get_available_models()
    
    print(f"   OpenAI API Key: {'✅ Configured' if api_key_configured else '❌ Not Set'}")
    print(f"   OpenAI Available: {'✅ Yes' if is_available else '❌ No'}")
    
    if not api_key_configured:
        print("   💡 To enable OpenAI: Set OPENAI_API_KEY environment variable")
        print("   Example: export OPENAI_API_KEY='your-api-key-here'")
    elif not is_available:
        print("   ⚠️ API key configured but OpenAI API not accessible")
    else:
        print(f"   Current Model: {llm_service.model_name}")
        if models:
            print(f"   Available Models: {models[:3]}...")
    
    print("\n🤖 Testing Chat Responses:")
    print("-" * 30)
    
    # Test messages
    test_messages = [
        "Hello there!",
        "Which ISTQB certification should I start with?",
        "Tell me about the weather",  # Off-topic to test redirection
        "I have 3 years of testing experience, what should I do next?",
        "What's the difference between CTAL-TA and CTAL-TM?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. User: {message}")
        
        try:
            response = llm_service.generate_response(message)
            
            # Truncate long responses for readability
            bot_message = response['message']
            if len(bot_message) > 120:
                bot_message = bot_message[:120] + "..."
            
            source = response.get('source', 'rule-based')
            tokens = response.get('tokens_used', 'N/A')
            
            print(f"   Bot ({source}): {bot_message}")
            print(f"   Intent: {response['intent']}")
            print(f"   Suggestions: {response['suggestions'][:2]}...")  # Show first 2 suggestions
            if tokens != 'N/A':
                print(f"   Tokens Used: {tokens}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Test completed!")
    status = "OpenAI LLM Active" if is_available else "Fallback Mode (Rule-based)"
    print(f"🎯 Integration Status: {status}")
    
    if is_available:
        print("\n🚀 OpenAI integration is working! The chatbot will use GPT for intelligent responses.")
    else:
        print("\n📋 Using fallback responses. Set OPENAI_API_KEY to enable AI-powered conversations.")

if __name__ == "__main__":
    test_openai_integration()
