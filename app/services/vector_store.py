class VectorStore:
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
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts into vectors using SentenceTransformer
        
        Args:
            texts: List of texts to encode
            
        Returns:
            Numpy array of vectors
        """
        if not self.encoder:
            raise RuntimeError("SentenceTransformer not available")
        
        try:
            # Encode texts
            embeddings = self.encoder.encode(texts, convert_to_numpy=True)
            
            # Normalize vectors for cosine similarity
            faiss.normalize_L2(embeddings)
            
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise
    
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
            texts = []
            doc_metadata = []
            doc_ids = []
            
            for doc in documents:
                if 'text' not in doc or not doc['text']:
                    continue
                
                # Generate document ID
                doc_id = doc.get('id', f"doc_{len(self.documents)}_{datetime.now().timestamp()}")
                
                texts.append(doc['text'])
                
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
            
            if not texts:
                return []
            
            # Encode texts
            embeddings = self.encode_texts(texts)
            
            # Add to FAISS index
            self.index.add(embeddings.astype(np.float32))
            
            # Update document storage
            start_idx = len(self.documents)
            self.documents.extend(doc_metadata)
            
            # Update document map
            for i, doc_id in enumerate(doc_ids):
                self.document_map[doc_id] = start_idx + i
            
            logger.info(f"✅ Added {len(doc_ids)} documents to vector store")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(self, 
               query: str, 
               top_k: int = 5, 
               threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar documents with scores
        """
        if not self.documents or not query:
            return []
        
        try:
            # Encode query
            query_embedding = self.encode_texts([query])
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding.astype(np.float32), top_k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                
                if score < threshold:
                    continue
                
                # Get document metadata
                doc = self.documents[idx].copy()
                doc['similarity_score'] = float(score)
                doc['rank'] = i + 1
                
                results.append(doc)
            
            return results
            
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
        
        return self.search(doc['text'], top_k + 1)[1:]  # Exclude the document itself
    
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
            # Note: FAISS doesn't support deletion, so we mark as deleted
            idx = self.document_map[doc_id]
            self.documents[idx]['deleted'] = True
            self.documents[idx]['deleted_at'] = datetime.now().isoformat()
            
            # Remove from document map
            del self.document_map[doc_id]
            
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
            'index_size': self.index.ntotal,
            'vector_dimension': self.dimension,
            'model_name': self.model_name,
            'storage_path': self.vector_store_path
        }
    
    def save_vector_store(self) -> bool:
        """
        Save vector store to disk
        
        Returns:
            True if saved successfully
        """
        try:
            # Save FAISS index
            index_path = os.path.join(self.vector_store_path, "faiss_index.idx")
            faiss.write_index(self.index, index_path)
            
            # Save documents metadata
            docs_path = os.path.join(self.vector_store_path, "documents.pkl")
            with open(docs_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'document_map': self.document_map,
                    'metadata': {
                        'model_name': self.model_name,
                        'dimension': self.dimension,
                        'saved_at': datetime.now().isoformat()
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
            index_path = os.path.join(self.vector_store_path, "faiss_index.idx")
            docs_path = os.path.join(self.vector_store_path, "documents.pkl")
            
            if not (os.path.exists(index_path) and os.path.exists(docs_path)):
                logger.info("No existing vector store found, starting fresh")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load documents metadata
            with open(docs_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.document_map = data['document_map']
                metadata = data.get('metadata', {})
            
            logger.info(f"✅ Vector store loaded: {len(self.documents)} documents, "
                       f"model: {metadata.get('model_name', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def rebuild_index(self) -> bool:
        """
        Rebuild FAISS index from scratch (useful after many deletions)
        
        Returns:
            True if rebuilt successfully
        """
        try:
            # Get active documents
            active_docs = [doc for doc in self.documents if not doc.get('deleted', False)]
            
            if not active_docs:
                # Create empty index
                self.index = faiss.IndexFlatIP(self.dimension)
                self.documents = []
                self.document_map = {}
                return True
            
            # Extract texts
            texts = [doc['text'] for doc in active_docs]
            
            # Create new index
            embeddings = self.encode_texts(texts)
            new_index = faiss.IndexFlatIP(self.dimension)
            new_index.add(embeddings.astype(np.float32))
            
            # Update data structures
            self.index = new_index
            self.documents = active_docs
            self.document_map = {doc['id']: i for i, doc in enumerate(active_docs)}
            
            # Update index positions
            for i, doc in enumerate(self.documents):
                doc['index_position'] = i
            
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
            self.index = faiss.IndexFlatIP(self.dimension)
            self.documents = []
            self.document_map = {}
            
            logger.info("✅ Vector store cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            return False


# Global vector store instance
vector_store = VectorStore()
