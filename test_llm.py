#!/usr/bin/env python3
"""
Quick test script to verify LLM integration
"""

from app.services.llm_service import llm_service

def test_llm_integration():
    print("🧪 Testing LLM Integration for ISTQB Chatbot")
    print("=" * 50)
    
    # Check if OpenAI is available
    print(f"🔍 Checking OpenAI API status...")
    is_available = llm_service.is_available()
    print(f"   OpenAI API Available: {'✅ Yes' if is_available else '❌ No'}")
    
    if is_available:
        models = llm_service.get_available_models()
        print(f"   Available Models: {models}")
        print(f"   Current Model: {llm_service.model_name}")
    else:
        print("   💡 To enable LLM: Set your OPENAI_API_KEY environment variable")
    
    print("\n🤖 Testing Chat Responses:")
    print("-" * 30)
    
    test_messages = [
        "Hello there!",
        "Which ISTQB certification should I start with?",
        "Tell me about the weather",
        "I have 3 years of testing experience, what should I do next?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. User: {message}")
        try:
            response = llm_service.generate_response(message)
            source = response.get('source', 'rule-based')
            print(f"   Bot ({source}): {response['message'][:100]}...")
            print(f"   Intent: {response['intent']}")
            print(f"   Suggestions: {response.get('suggestions', [])[:2]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Test completed!")
    print(f"🎯 Integration Status: {'LLM Active' if is_available else 'Fallback Mode'}")

if __name__ == "__main__":
    test_llm_integration()
