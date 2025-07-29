#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Demonstration Script
Shows how the ISTQB chatbot uses knowledge base retrieval to enhance responses
"""

from app.services.rag_service import rag_service
from app.services.llm_service import llm_service


def test_rag_retrieval():
    """Test knowledge base retrieval functionality"""
    print("🔍 RAG (Retrieval-Augmented Generation) Demonstration")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "What is ISTQB?",
        "How much does ISTQB certification cost?",
        "Tell me about Foundation Level certification",
        "What are the exam requirements?",
        "How long does it take to study?",
        "What are the benefits of certification?",
        "Do I need to renew my certification?",
        "What are the seven testing principles?"
    ]
    
    print(f"📊 Knowledge Base Stats: {rag_service.get_stats()}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        
        # Get relevant content from knowledge base
        relevant_content = rag_service.retrieve_relevant_content(query, top_k=2)
        
        if relevant_content:
            print(f"✅ Found {len(relevant_content)} relevant entries:")
            for idx, content in enumerate(relevant_content, 1):
                print(f"  {idx}. [{content['type'].upper()}] {content.get('question', content.get('title', 'N/A'))}")
                print(f"      Score: {content['score']:.3f}")
                print(f"      ID: {content.get('id', 'N/A')}")
        else:
            print("❌ No relevant content found")
        
        # Get formatted context for LLM
        llm_context = rag_service.get_context_for_llm(query)
        if llm_context:
            print(f"📝 LLM Context Generated: {len(llm_context)} characters")
        else:
            print("📝 No LLM context generated")


def test_contextual_responses():
    """Test how RAG enhances chatbot responses"""
    print("\n\n🤖 RAG-Enhanced Contextual Responses")
    print("=" * 60)
    
    test_queries = [
        "What is ISTQB certification?",
        "How much does it cost to get certified?",
        "Tell me about the exam format",
        "What are the career benefits?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n💬 Example {i}: {query}")
        print("-" * 40)
        
        try:
            # Generate response using RAG
            response = llm_service.generate_response(query)
            
            print(f"🎯 Intent: {response['intent']}")
            print(f"📝 Response Source: {response.get('source', 'unknown')}")
            print(f"🔄 RAG Context Used: {response.get('rag_context_used', 'N/A')}")
            
            if response.get('retrieved_content'):
                print(f"📚 Retrieved Content IDs: {response['retrieved_content']}")
            
            print(f"💭 Response Preview: {response['message'][:150]}...")
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")


def test_knowledge_search():
    """Test direct knowledge base search functionality"""
    print("\n\n🔎 Direct Knowledge Base Search")
    print("=" * 60)
    
    # Search by category
    categories = ["general", "certifications", "career", "exam_info", "cost"]
    
    for category in categories:
        results = rag_service.search_by_category(category)
        print(f"📂 Category '{category}': {len(results)} entries")
    
    print()
    
    # Search by keywords
    keyword_searches = [
        ["Foundation Level", "CTFL"],
        ["Advanced Level", "CTAL"],
        ["cost", "price"],
        ["career", "salary"],
        ["exam", "questions"]
    ]
    
    for keywords in keyword_searches:
        results = rag_service.search_by_keywords(keywords)
        print(f"🏷️ Keywords {keywords}: {len(results)} matches")


if __name__ == "__main__":
    print("🚀 ISTQB Chatbot RAG System Test")
    print("Testing Retrieval-Augmented Generation functionality")
    print("=" * 80)
    
    # Test 1: Knowledge retrieval
    test_rag_retrieval()
    
    # Test 2: Contextual responses
    test_contextual_responses()
    
    # Test 3: Knowledge search
    test_knowledge_search()
    
    print("\n\n✅ RAG Demonstration Complete!")
    print("The system successfully retrieves relevant context from the knowledge base")
    print("and uses it to enhance both AI and rule-based responses.")
