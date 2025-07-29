import json
import os
from typing import List, Dict, Any, Tuple, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from .pdf_processor import pdf_processor
from .simple_vector_store import vector_store


class RAGService:
    """
    Retrieval-Augmented Generation service for ISTQB knowledge base
    """
    
    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self.load_knowledge_base()
        self.vectorizer = None
        self.faq_vectors = None
        self.doc_vectors = None
        self._initialize_vectors()
    
    def load_knowledge_base(self) -> Dict[str, Any]:
        """Load the knowledge base from JSON file"""
        try:
            kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), self.knowledge_base_path)
            with open(kb_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return {"faq": [], "documentation": {}}
    
    def ingest_pdfs(self, pdf_paths: List[str]) -> Dict[str, Union[List[str], str]]:
        """
        Ingest PDF files into the knowledge base and update vector store
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            Summary of ingestion results
        """
        results = {
            "processed_files": [],
            "errors": []
        }
        for pdf_path in pdf_paths:
            try:
                if not pdf_processor.validate_pdf(pdf_path):
                    raise ValueError(f"Invalid or unreadable PDF: {pdf_path}")
                
                # Process PDF to extract chunks
                processing_result = pdf_processor.process_pdf_file(pdf_path)
                if not processing_result.get("success", False):
                    results["errors"].append({"file": pdf_path, "error": processing_result.get("error", "Unknown error")})
                    continue
                
                # Add chunks to vector store
                document_ids = vector_store.add_documents(processing_result["chunks"])
                
                results["processed_files"].append(pdf_path)
                print(f"Processed {len(document_ids)} chunks from {pdf_path}")
                
            except Exception as e:
                error_message = str(e)
                results["errors"].append({"file": pdf_path, "error": error_message})
                print(f"Error processing {pdf_path}: {error_message}")
        
        # Save vector store updates
        vector_store.save_vector_store()
        return results
    def _initialize_vectors(self):
        """Initialize TF-IDF vectors for efficient retrieval"""
        try:
            # Prepare all text content for vectorization
            all_texts = []
            
            # Add FAQ questions and answers
            for faq in self.knowledge_base.get("faq", []):
                text = f"{faq['question']} {faq['answer']} {' '.join(faq.get('keywords', []))}"
                all_texts.append(text)
            
            # Add documentation content
            for doc_key, doc in self.knowledge_base.get("documentation", {}).items():
                text = f"{doc['title']} {doc['content']} {' '.join(doc.get('keywords', []))}"
                all_texts.append(text)
            
            if all_texts:
                # Create TF-IDF vectorizer
                self.vectorizer = TfidfVectorizer(
                    stop_words='english',
                    max_features=5000,
                    ngram_range=(1, 2),
                    lowercase=True
                )
                
                # Fit and transform all texts
                all_vectors = self.vectorizer.fit_transform(all_texts)
                
                # Split vectors back into FAQ and documentation
                faq_count = len(self.knowledge_base.get("faq", []))
                self.faq_vectors = all_vectors[:faq_count]
                self.doc_vectors = all_vectors[faq_count:]
                
                print(f"✅ RAG Service initialized with {faq_count} FAQs and {len(self.knowledge_base.get('documentation', {}))} documents")
            else:
                print("⚠️ No content found in knowledge base")
                
        except Exception as e:
            print(f"Error initializing vectors: {e}")
    
    def retrieve_relevant_content(self, query: str, top_k: int = 3, use_vector_store: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant content from knowledge base using both traditional and vector search
        
        Args:
            query: User's query
            top_k: Number of top results to return
            use_vector_store: Whether to include results from vector store
            
        Returns:
            List of relevant content with scores
        """
        relevant_content = []
        
        # Search in vector store first (PDF content and other documents)
        if use_vector_store:
            try:
                vector_results = vector_store.search(query, top_k=top_k, threshold=0.3)
                for result in vector_results:
                    result["type"] = "vector_document"
                    result["score"] = result.get("similarity_score", 0.0)
                    relevant_content.append(result)
            except Exception as e:
                print(f"Error in vector store search: {e}")
        
        # Search in traditional knowledge base (FAQ and documentation)
        if self.vectorizer:
            try:
                # Vectorize the query
                query_vector = self.vectorizer.transform([query.lower()])
                
                # Search in FAQ
                if self.faq_vectors is not None and self.faq_vectors.shape[0] > 0:
                    faq_similarities = cosine_similarity(query_vector, self.faq_vectors)[0]
                    
                    for idx, score in enumerate(faq_similarities):
                        if score > 0.1:  # Threshold for relevance
                            faq_item = self.knowledge_base["faq"][idx].copy()
                            faq_item["score"] = float(score)
                            faq_item["type"] = "faq"
                            relevant_content.append(faq_item)
                
                # Search in documentation
                if self.doc_vectors is not None and self.doc_vectors.shape[0] > 0:
                    doc_similarities = cosine_similarity(query_vector, self.doc_vectors)[0]
                    doc_items = list(self.knowledge_base.get("documentation", {}).items())
                    
                    for idx, score in enumerate(doc_similarities):
                        if score > 0.1:  # Threshold for relevance
                            doc_key, doc_item = doc_items[idx]
                            doc_content = doc_item.copy()
                            doc_content["score"] = float(score)
                            doc_content["type"] = "documentation"
                            relevant_content.append(doc_content)
                
            except Exception as e:
                print(f"Error in traditional retrieval: {e}")
        
        # Sort by relevance score and return top_k
        relevant_content.sort(key=lambda x: x["score"], reverse=True)
        return relevant_content[:top_k]
    
    def get_context_for_llm(self, query: str, max_context_length: int = 1500) -> str:
        """
        Get formatted context for LLM prompt
        
        Args:
            query: User's query
            max_context_length: Maximum length of context to include
            
        Returns:
            Formatted context string
        """
        relevant_content = self.retrieve_relevant_content(query, top_k=3)
        
        if not relevant_content:
            return ""
        
        context_parts = ["## Relevant ISTQB Information:"]
        current_length = len(context_parts[0])
        
        for item in relevant_content:
            if item["type"] == "faq":
                part = f"\\n**Q: {item['question']}**\\nA: {item['answer']}"
            else:  # documentation
                part = f"\\n**{item['title']}**\\n{item['content']}"
            
            if current_length + len(part) < max_context_length:
                context_parts.append(part)
                current_length += len(part)
            else:
                break
        
        return "\\n".join(context_parts)
    
    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Search FAQs by category
        
        Args:
            category: Category to search for
            
        Returns:
            List of FAQs in the category
        """
        return [faq for faq in self.knowledge_base.get("faq", []) 
                if faq.get("category", "").lower() == category.lower()]
    
    def search_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Search content by keywords
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of matching content
        """
        results = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        # Search in FAQ
        for faq in self.knowledge_base.get("faq", []):
            faq_keywords = [kw.lower() for kw in faq.get("keywords", [])]
            if any(kw in faq_keywords for kw in keywords_lower):
                faq_copy = faq.copy()
                faq_copy["type"] = "faq"
                results.append(faq_copy)
        
        # Search in documentation
        for doc_key, doc in self.knowledge_base.get("documentation", {}).items():
            doc_keywords = [kw.lower() for kw in doc.get("keywords", [])]
            if any(kw in doc_keywords for kw in keywords_lower):
                doc_copy = doc.copy()
                doc_copy["type"] = "documentation"
                results.append(doc_copy)
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get knowledge base statistics"""
        return {
            "total_faqs": len(self.knowledge_base.get("faq", [])),
            "total_documents": len(self.knowledge_base.get("documentation", {})),
            "categories": len(set(faq.get("category", "") for faq in self.knowledge_base.get("faq", []))),
            "total_entries": len(self.knowledge_base.get("faq", [])) + len(self.knowledge_base.get("documentation", {}))
        }


# Global RAG service instance
rag_service = RAGService()
