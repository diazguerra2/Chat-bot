import os
import logging
from typing import List, Dict, Any, Optional
import PyPDF2
from datetime import datetime
import hashlib
import re

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Service for processing PDF files and extracting structured text content
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # overlap between chunks
    
    def extract_text_from_pdf(self, pdf_path: str, method: str = "pypdf2") -> Dict[str, Any]:
        """
        Extract text from PDF using different methods
        
        Args:
            pdf_path: Path to the PDF file
            method: Extraction method ('pdfplumber' or 'pypdf2')
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            if method == "pypdf2":
                return self._extract_with_pypdf2(pdf_path)
            else:
                raise ValueError(f"Unsupported extraction method: {method}")
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return {
                "text": "",
                "pages": [],
                "metadata": {},
                "error": str(e)
            }
    
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text using PyPDF2 (simpler, faster for basic PDFs)"""
        pages_text = []
        full_text = ""
        metadata = {}
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                    "creator": pdf_reader.metadata.get("/Creator", ""),
                    "producer": pdf_reader.metadata.get("/Producer", ""),
                    "creation_date": pdf_reader.metadata.get("/CreationDate", ""),
                    "modification_date": pdf_reader.metadata.get("/ModDate", "")
                }
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        page_text = self._clean_text(page_text)
                        pages_text.append({
                            "page_number": page_num,
                            "text": page_text,
                            "char_count": len(page_text)
                        })
                        full_text += f"\n--- Page {page_num} ---\n{page_text}\n"
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    continue
        
        return {
            "text": full_text.strip(),
            "pages": pages_text,
            "metadata": metadata,
            "total_pages": len(pages_text),
            "total_chars": len(full_text),
            "extraction_method": "pypdf2"
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\r\n|\r|\n', '\n', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks for better RAG performance
        
        Args:
            text: Text to chunk
            metadata: Additional metadata to include with each chunk
            
        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If not at the end, try to break at a sentence or paragraph boundary
            if end < len(text):
                # Look for paragraph break first
                para_break = text.rfind('\n\n', start, end)
                if para_break != -1 and para_break > start + self.chunk_size // 2:
                    end = para_break + 2
                else:
                    # Look for sentence break
                    sent_break = text.rfind('. ', start, end)
                    if sent_break != -1 and sent_break > start + self.chunk_size // 2:
                        end = sent_break + 2
                    else:
                        # Look for word boundary
                        word_break = text.rfind(' ', start, end)
                        if word_break != -1 and word_break > start + self.chunk_size // 2:
                            end = word_break
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_data = {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                    "start_pos": start,
                    "end_pos": end,
                    "chunk_hash": hashlib.md5(chunk_text.encode()).hexdigest()
                }
                
                # Add metadata if provided
                if metadata:
                    chunk_data["metadata"] = metadata.copy()
                
                chunks.append(chunk_data)
                chunk_id += 1
            
            # Move start position with overlap
            start = max(start + self.chunk_size - self.chunk_overlap, end)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def process_pdf_file(self, pdf_path: str, source_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete PDF processing pipeline: extract, clean, and chunk
        
        Args:
            pdf_path: Path to PDF file
            source_info: Additional source information
            
        Returns:
            Structured data ready for RAG ingestion
        """
        try:
            # Extract text from PDF
            extraction_result = self.extract_text_from_pdf(pdf_path)
            
            if "error" in extraction_result:
                return extraction_result
            
            # Generate file hash for deduplication
            file_hash = self._get_file_hash(pdf_path)
            
            # Prepare source metadata
            source_metadata = {
                "source_file": os.path.basename(pdf_path),
                "source_path": pdf_path,
                "file_size": os.path.getsize(pdf_path),
                "file_hash": file_hash,
                "processed_at": datetime.now().isoformat(),
                "extraction_method": extraction_result["extraction_method"],
                "total_pages": extraction_result["total_pages"],
                "total_chars": extraction_result["total_chars"]
            }
            
            # Add PDF metadata
            source_metadata.update(extraction_result["metadata"])
            
            # Add custom source info
            if source_info:
                source_metadata.update(source_info)
            
            # Chunk the text
            chunks = self.chunk_text(extraction_result["text"], source_metadata)
            
            return {
                "success": True,
                "source_metadata": source_metadata,
                "chunks": chunks,
                "total_chunks": len(chunks),
                "raw_text": extraction_result["text"],
                "pages": extraction_result["pages"]
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_file": os.path.basename(pdf_path) if pdf_path else "unknown"
            }
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate MD5 hash of file for deduplication"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error generating file hash: {e}")
            return ""
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return self.supported_formats.copy()
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """Validate if file is a readable PDF"""
        try:
            if not os.path.exists(pdf_path):
                return False
            
            if not pdf_path.lower().endswith('.pdf'):
                return False
            
            # Try to open with PyPDF2 to verify it's a valid PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages) > 0
                
        except Exception:
            return False


# Global PDF processor instance
pdf_processor = PDFProcessor()
