import os
import logging
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import PyPDF2
from datetime import datetime
import hashlib
import re
import tempfile
import io
from concurrent.futures import ThreadPoolExecutor
import gc

logger = logging.getLogger(__name__)


class EnhancedPDFProcessor:
    """
    Enhanced PDF processor for handling massive PDF files with streaming and memory-efficient processing
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # overlap between chunks
        self.max_file_size = 100 * 1024 * 1024  # 100 MB default limit
        self.pages_per_batch = 10  # Process in batches to manage memory
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def validate_pdf_file(self, file_path: str, max_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Validate PDF file before processing
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": False,
            "file_size": 0,
            "error": None,
            "estimated_pages": 0
        }
        
        try:
            if not os.path.exists(file_path):
                validation["error"] = "File not found"
                return validation
            
            if not file_path.lower().endswith('.pdf'):
                validation["error"] = "Not a PDF file"
                return validation
            
            # Check file size
            file_size = os.path.getsize(file_path)
            validation["file_size"] = file_size
            
            max_allowed = max_size or self.max_file_size
            if file_size > max_allowed:
                validation["error"] = f"File too large: {file_size / (1024*1024):.1f}MB (max: {max_allowed / (1024*1024):.1f}MB)"
                return validation
            
            # Quick PDF validation
            with open(file_path, 'rb') as file:
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    validation["estimated_pages"] = len(pdf_reader.pages)
                    validation["valid"] = True
                except Exception as e:
                    validation["error"] = f"Invalid PDF file: {str(e)}"
                    
        except Exception as e:
            validation["error"] = f"Validation error: {str(e)}"
        
        return validation
    
    async def extract_text_streaming(self, pdf_path: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Extract text from PDF in streaming batches to handle massive files
        
        Yields:
            Dictionary containing batch information and extracted text
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Process in batches
                for batch_start in range(0, total_pages, self.pages_per_batch):
                    batch_end = min(batch_start + self.pages_per_batch, total_pages)
                    
                    # Extract text from current batch
                    batch_result = await self._process_page_batch(
                        pdf_reader, batch_start, batch_end, total_pages
                    )
                    
                    yield batch_result
                    
                    # Force garbage collection to free memory
                    gc.collect()
                    
        except Exception as e:
            logger.error(f"Error in streaming extraction: {e}")
            yield {
                "batch_number": 0,
                "pages_processed": 0,
                "total_pages": 0,
                "text": "",
                "error": str(e),
                "progress": 0.0
            }
    
    async def _process_page_batch(self, pdf_reader, start_page: int, end_page: int, total_pages: int) -> Dict[str, Any]:
        """
        Process a batch of pages in a separate thread
        """
        def extract_batch():
            batch_text = ""
            pages_data = []
            
            for page_num in range(start_page, end_page):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text:
                        cleaned_text = self._clean_text(page_text)
                        pages_data.append({
                            "page_number": page_num + 1,
                            "text": cleaned_text,
                            "char_count": len(cleaned_text)
                        })
                        batch_text += f"\n--- Page {page_num + 1} ---\n{cleaned_text}\n"
                        
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num + 1}: {e}")
                    continue
            
            return {
                "batch_number": (start_page // self.pages_per_batch) + 1,
                "pages_processed": end_page - start_page,
                "total_pages": total_pages,
                "start_page": start_page + 1,
                "end_page": end_page,
                "text": batch_text.strip(),
                "pages_data": pages_data,
                "progress": (end_page / total_pages) * 100
            }
        
        # Run extraction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, extract_batch)
        return result
    
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
    
    def chunk_text_advanced(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Advanced text chunking with better boundary detection
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        # Split by double newlines first (paragraphs)
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size:
                # If we have content, save it as a chunk
                if current_chunk.strip():
                    chunk_data = {
                        "chunk_id": chunk_id,
                        "text": current_chunk.strip(),
                        "char_count": len(current_chunk.strip()),
                        "chunk_hash": hashlib.md5(current_chunk.strip().encode()).hexdigest()
                    }
                    
                    if metadata:
                        chunk_data["metadata"] = metadata.copy()
                    
                    chunks.append(chunk_data)
                    chunk_id += 1
                
                # Start new chunk with current paragraph
                current_chunk = paragraph
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunk_data = {
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "char_count": len(current_chunk.strip()),
                "chunk_hash": hashlib.md5(current_chunk.strip().encode()).hexdigest()
            }
            
            if metadata:
                chunk_data["metadata"] = metadata.copy()
            
            chunks.append(chunk_data)
        
        return chunks
    
    async def process_massive_pdf(self, pdf_path: str, 
                                 source_info: Dict[str, Any] = None,
                                 progress_callback=None) -> Dict[str, Any]:
        """
        Process massive PDF files with progress tracking
        
        Args:
            pdf_path: Path to PDF file
            source_info: Additional source information
            progress_callback: Optional callback for progress updates
            
        Returns:
            Processing results with chunks
        """
        try:
            # Validate file first
            validation = await self.validate_pdf_file(pdf_path)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"],
                    "file_info": validation
                }
            
            # Generate file hash
            file_hash = await self._get_file_hash_async(pdf_path)
            
            # Prepare source metadata
            source_metadata = {
                "source_file": os.path.basename(pdf_path),
                "source_path": pdf_path,
                "file_size": validation["file_size"],
                "file_hash": file_hash,
                "processed_at": datetime.now().isoformat(),
                "extraction_method": "enhanced_streaming",
                "estimated_pages": validation["estimated_pages"]
            }
            
            if source_info:
                source_metadata.update(source_info)
            
            # Process file in streaming batches
            all_chunks = []
            all_text = ""
            total_pages_processed = 0
            
            async for batch in self.extract_text_streaming(pdf_path):
                if "error" in batch:
                    return {
                        "success": False,
                        "error": batch["error"],
                        "source_metadata": source_metadata
                    }
                
                # Update progress
                total_pages_processed += batch["pages_processed"]
                if progress_callback:
                    await progress_callback({
                        "stage": "extraction",
                        "progress": batch["progress"],
                        "pages_processed": total_pages_processed,
                        "total_pages": batch["total_pages"],
                        "batch_number": batch["batch_number"]
                    })
                
                # Accumulate text and chunk it
                batch_text = batch["text"]
                all_text += batch_text
                
                # Chunk the batch text
                batch_chunks = self.chunk_text_advanced(batch_text, source_metadata)
                all_chunks.extend(batch_chunks)
                
                # Optional: Save intermediate results for very large files
                if len(all_chunks) > 1000:  # Every 1000 chunks
                    logger.info(f"Processed {len(all_chunks)} chunks so far...")
            
            # Update final metadata
            source_metadata["total_pages"] = total_pages_processed
            source_metadata["total_chars"] = len(all_text)
            source_metadata["total_chunks"] = len(all_chunks)
            
            return {
                "success": True,
                "source_metadata": source_metadata,
                "chunks": all_chunks,
                "total_chunks": len(all_chunks),
                "file_info": validation
            }
            
        except Exception as e:
            logger.error(f"Error processing massive PDF {pdf_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_file": os.path.basename(pdf_path) if pdf_path else "unknown"
            }
    
    async def _get_file_hash_async(self, file_path: str) -> str:
        """Generate MD5 hash of file asynchronously"""
        def compute_hash():
            hash_md5 = hashlib.md5()
            try:
                with open(file_path, "rb") as f:
                    while chunk := f.read(8192):  # Read in 8KB chunks
                        hash_md5.update(chunk)
                return hash_md5.hexdigest()
            except Exception as e:
                logger.error(f"Error generating file hash: {e}")
                return ""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, compute_hash)
    
    def get_memory_usage_estimate(self, file_size_bytes: int) -> Dict[str, float]:
        """
        Estimate memory usage for processing a PDF file
        
        Returns:
            Memory estimates in MB
        """
        # Rough estimates based on typical PDF text density
        estimated_text_size = file_size_bytes * 0.1  # Assume 10% is extractable text
        processing_overhead = estimated_text_size * 2  # 2x overhead for processing
        
        return {
            "file_size_mb": file_size_bytes / (1024 * 1024),
            "estimated_text_mb": estimated_text_size / (1024 * 1024),
            "estimated_memory_mb": processing_overhead / (1024 * 1024),
            "recommended_batch_size": max(5, min(20, int(100 / (processing_overhead / (1024 * 1024)))))
        }
    
    def __del__(self):
        """Cleanup thread pool on destruction"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# Global enhanced PDF processor instance
enhanced_pdf_processor = EnhancedPDFProcessor()
