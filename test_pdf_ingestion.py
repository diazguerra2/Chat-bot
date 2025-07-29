#!/usr/bin/env python3
"""
Simple test script for PDF ingestion functionality
"""

import os
import sys

def test_pdf_ingestion():
    """Test PDF ingestion with a sample file"""
    try:
        from app.services.rag_service import rag_service
        from app.services.simple_vector_store import vector_store
        
        print("🧪 Testing PDF Ingestion System")
        print("=" * 50)
        
        # Test if services are available
        print("✅ RAG Service loaded successfully")
        print("✅ Vector Store loaded successfully")
        
        # Show initial statistics
        print("\n📊 Initial Statistics:")
        vector_stats = vector_store.get_stats()
        print(f"   - Active documents: {vector_stats['active_documents']}")
        print(f"   - Total documents: {vector_stats['total_documents']}")
        print(f"   - Is fitted: {vector_stats['is_fitted']}")
        
        # Test with a sample PDF (you need to provide this)
        sample_pdf_path = "sample.pdf"  # Change this to an actual PDF file path
        
        if os.path.exists(sample_pdf_path):
            print(f"\n📄 Processing PDF: {sample_pdf_path}")
            
            # Ingest the PDF
            results = rag_service.ingest_pdfs([sample_pdf_path])
            
            print("\n📋 Processing Results:")
            print(f"   - Processed files: {len(results['processed_files'])}")
            print(f"   - Errors: {len(results['errors'])}")
            
            if results['processed_files']:
                print(f"   ✅ Successfully processed: {results['processed_files']}")
            
            if results['errors']:
                print(f"   ❌ Errors encountered:")
                for error in results['errors']:
                    print(f"      - {error['file']}: {error['error']}")
            
            # Show updated statistics
            print("\n📊 Updated Statistics:")
            vector_stats = vector_store.get_stats()
            print(f"   - Active documents: {vector_stats['active_documents']}")
            print(f"   - Total documents: {vector_stats['total_documents']}")
            print(f"   - Is fitted: {vector_stats['is_fitted']}")
            print(f"   - Vocabulary size: {vector_stats['vectorizer_vocabulary_size']}")
            
            # Test search functionality
            print("\n🔍 Testing Search Functionality:")
            test_query = "ISTQB Foundation Level"
            search_results = vector_store.search(test_query, top_k=3)
            
            print(f"   Query: '{test_query}'")
            print(f"   Results found: {len(search_results)}")
            
            for i, result in enumerate(search_results, 1):
                print(f"   {i}. Score: {result['similarity_score']:.4f}")
                print(f"      Text preview: {result['text'][:100]}...")
                print()
        
        else:
            print(f"\n⚠️  Sample PDF not found: {sample_pdf_path}")
            print("   Please create a sample PDF file or update the path in the script")
            print("\n   You can still test the basic functionality:")
            
            # Test with dummy data
            dummy_docs = [
                {
                    "text": "This is a sample document about ISTQB Foundation Level certification.",
                    "source": "test",
                    "title": "Sample Document 1"
                },
                {
                    "text": "Advanced testing techniques are covered in ISTQB Advanced Level certifications.",
                    "source": "test", 
                    "title": "Sample Document 2"
                }
            ]
            
            print("\n📝 Adding dummy documents for testing...")
            doc_ids = vector_store.add_documents(dummy_docs)
            print(f"   Added documents: {doc_ids}")
            
            # Test search with dummy data
            print("\n🔍 Testing Search with Dummy Data:")
            test_query = "ISTQB Foundation"
            search_results = vector_store.search(test_query, top_k=2)
            
            print(f"   Query: '{test_query}'")
            print(f"   Results found: {len(search_results)}")
            
            for i, result in enumerate(search_results, 1):
                print(f"   {i}. Score: {result['similarity_score']:.4f}")
                print(f"      Text: {result['text']}")
                print()
        
        print("✅ Test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this from the project root directory")
        print("   and that all dependencies are installed (pip install -r requirements.txt)")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pdf_ingestion()
