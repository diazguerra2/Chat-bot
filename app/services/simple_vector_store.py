import os
import json
import pickle
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """
    Simple vector store using TF-IDF for similarity search
    """
    
    def __init__(self, vector_store_path: str = "data/vector_store"):
        """
        Initialize vector store
        
        Args:
            vector_store_path: Directory to store vector data
        """
        self.vector_store_path = vector_store_path
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2),
            lowercase=True
        )
        
        self.documents = []  # Store document metadata
        self.document_map = {}  # Map document IDs to indices
        self.vectors = None  # Store TF-IDF vectors
        self.is_fitted = False
        
        # Create storage directory
        os.makedirs(vector_store_path, exist_ok=True)
        
        # Load existing data if available
        self.load_vector_store()
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            documents: List of documents with 'text' and metadata
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        try:
            # Extract texts and prepare metadata
            doc_metadata = []
            doc_ids = []
            
            for doc in documents:
                if 'text' not in doc or not doc['text']:
                    continue
                
                # Generate document ID
                doc_id = doc.get('id', f"doc_{len(self.documents)}_{datetime.now().timestamp()}")
                
                # Prepare document metadata
                metadata = {
                    'id': doc_id,
                    'text': doc['text'],
                    'added_at': datetime.now().isoformat(),
                    'index_position': len(self.documents)
                }
                
                # Add any additional metadata
                for key, value in doc.items():
                    if key != 'text':
                        metadata[key] = value
                
                doc_metadata.append(metadata)
                doc_ids.append(doc_id)
            
            if not doc_metadata:
                return []
            
            # Update document storage
            start_idx = len(self.documents)
            self.documents.extend(doc_metadata)
            
            # Update document map
            for i, doc_id in enumerate(doc_ids):
                self.document_map[doc_id] = start_idx + i
            
            # Re-fit the vectorizer with all documents
            self._refit_vectorizer()
            
            logger.info(f"✅ Added {len(doc_ids)} documents to vector store")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def _refit_vectorizer(self):
        """Re-fit the TF-IDF vectorizer with all current documents"""
        if not self.documents:
            self.vectors = None
            self.is_fitted = False
            return
        
        try:
            # Get all document texts
            texts = [doc['text'] for doc in self.documents if not doc.get('deleted', False)]
            
            if texts:
                # Fit and transform all texts
                self.vectors = self.vectorizer.fit_transform(texts)
                self.is_fitted = True
                logger.info(f"✅ TF-IDF vectorizer fitted with {len(texts)} documents")
            else:
                self.vectors = None
                self.is_fitted = False
                
        except Exception as e:
            logger.error(f"Error fitting vectorizer: {e}")
            self.vectors = None
            self.is_fitted = False
    
    def search(self, 
               query: str, 
               top_k: int = 5, 
               threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar documents with scores
        """
        if not self.documents or not query or not self.is_fitted:
            return []
        
        try:
            # Transform query using fitted vectorizer
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.vectors)[0]
            
            # Get active documents (not deleted)
            active_docs = [doc for doc in self.documents if not doc.get('deleted', False)]
            
            # Create results with scores
            results = []
            for i, (doc, score) in enumerate(zip(active_docs, similarities)):
                if score >= threshold:
                    result_doc = doc.copy()
                    result_doc['similarity_score'] = float(score)
                    results.append(result_doc)
            
            # Sort by similarity score (descending)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Add rank information
            for i, result in enumerate(results[:top_k]):
                result['rank'] = i + 1
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def search_by_document_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document metadata if found
        """
        if doc_id in self.document_map:
            idx = self.document_map[doc_id]
            if idx < len(self.documents):
                return self.documents[idx].copy()
        return None
    
    def get_similar_documents(self, 
                            doc_id: str, 
                            top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document
        
        Args:
            doc_id: Reference document ID
            top_k: Number of similar documents to return
            
        Returns:
            List of similar documents
        """
        doc = self.search_by_document_id(doc_id)
        if not doc:
            return []
        
        # Search using the document's text, but exclude the document itself
        results = self.search(doc['text'], top_k + 1)
        return [r for r in results if r['id'] != doc_id][:top_k]
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document from vector store
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if deleted successfully
        """
        if doc_id not in self.document_map:
            return False
        
        try:
            idx = self.document_map[doc_id]
            if idx < len(self.documents):
                self.documents[idx]['deleted'] = True
                self.documents[idx]['deleted_at'] = datetime.now().isoformat()
                
                # Remove from document map
                del self.document_map[doc_id]
                
                # Re-fit vectorizer without deleted documents
                self._refit_vectorizer()
                
                logger.info(f"✅ Marked document {doc_id} as deleted")
                return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics
        
        Returns:
            Statistics dictionary
        """
        active_docs = [doc for doc in self.documents if not doc.get('deleted', False)]
        deleted_docs = [doc for doc in self.documents if doc.get('deleted', False)]
        
        return {
            'total_documents': len(self.documents),
            'active_documents': len(active_docs),
            'deleted_documents': len(deleted_docs),
            'is_fitted': self.is_fitted,
            'vectorizer_vocabulary_size': len(self.vectorizer.vocabulary_) if self.is_fitted else 0,
            'storage_path': self.vector_store_path
        }
    
    def save_vector_store(self) -> bool:
        """
        Save vector store to disk
        
        Returns:
            True if saved successfully
        """
        try:
            # Save all data
            data_path = os.path.join(self.vector_store_path, "vector_store.pkl")
            with open(data_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'document_map': self.document_map,
                    'vectorizer': self.vectorizer,
                    'vectors': self.vectors,
                    'is_fitted': self.is_fitted,
                    'metadata': {
                        'saved_at': datetime.now().isoformat(),
                        'total_documents': len(self.documents)
                    }
                }, f)
            
            logger.info(f"✅ Vector store saved to {self.vector_store_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            return False
    
    def load_vector_store(self) -> bool:
        """
        Load vector store from disk
        
        Returns:
            True if loaded successfully
        """
        try:
            data_path = os.path.join(self.vector_store_path, "vector_store.pkl")
            
            if not os.path.exists(data_path):
                logger.info("No existing vector store found, starting fresh")
                return False
            
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data.get('documents', [])
                self.document_map = data.get('document_map', {})
                self.vectorizer = data.get('vectorizer', TfidfVectorizer(
                    stop_words='english',
                    max_features=5000,
                    ngram_range=(1, 2),
                    lowercase=True
                ))
                self.vectors = data.get('vectors')
                self.is_fitted = data.get('is_fitted', False)
                metadata = data.get('metadata', {})
            
            logger.info(f"✅ Vector store loaded: {len(self.documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def rebuild_index(self) -> bool:
        """
        Rebuild the index from scratch (useful after many deletions)
        
        Returns:
            True if rebuilt successfully
        """
        try:
            # Get active documents
            active_docs = [doc for doc in self.documents if not doc.get('deleted', False)]
            
            # Reset everything
            self.documents = active_docs
            self.document_map = {doc['id']: i for i, doc in enumerate(active_docs)}
            
            # Update index positions
            for i, doc in enumerate(self.documents):
                doc['index_position'] = i
            
            # Re-fit vectorizer
            self._refit_vectorizer()
            
            logger.info(f"✅ Index rebuilt with {len(active_docs)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Clear all documents and index
        
        Returns:
            True if cleared successfully
        """
        try:
            self.documents = []
            self.document_map = {}
            self.vectors = None
            self.is_fitted = False
            
            # Reset vectorizer
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=5000,
                ngram_range=(1, 2),
                lowercase=True
            )
            
            logger.info("✅ Vector store cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            return False


# Global vector store instance
vector_store = SimpleVectorStore()
