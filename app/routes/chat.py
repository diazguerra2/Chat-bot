from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from app.models import ChatMessage, ChatResponse
from app.middleware.auth import verify_token
from app.services.llm_service import llm_service
from datetime import datetime
import uuid
import os
import tempfile
from typing import List

# Initialize router object
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage, current_user: dict = Depends(verify_token)):
    """Send message to chatbot and get a response"""
    print("="*50)
    print("CHAT ENDPOINT CALLED!")
    print("="*50)
    try:
        # Generate session ID if not provided
        current_session_id = chat_message.sessionId or str(uuid.uuid4())

        # Log the conversation (in production, store in a database)
        print(f"Chat - User {current_user['userId']}: {chat_message.message}")

        # Use LLM service for natural conversation with ISTQB knowledge
        print(f"[DEBUG] Calling LLM service with message: {chat_message.message}")
        bot_response = llm_service.generate_response(
            message=chat_message.message,
            context=f"User ID: {current_user['userId']}, Session: {current_session_id}"
        )
        print(f"[DEBUG] LLM response keys: {list(bot_response.keys())}")
        print(f"[DEBUG] LLM response source: {bot_response.get('source', 'NOT SET')}")
        print(f"[DEBUG] LLM response tokens: {bot_response.get('tokens_used', 'NOT SET')}")

        # Prepare response object
        response = ChatResponse(
            sessionId=current_session_id,
            message=bot_response['message'],
            intent=bot_response['intent'],
            suggestions=bot_response.get('suggestions', []),
            timestamp=datetime.now().isoformat(),
            source=bot_response.get('source'),
            tokens_used=bot_response.get('tokens_used'),
            retrieved_content=bot_response.get('retrieved_content', []),
            rag_context_used=bot_response.get('rag_context_used')
        )

        return response

    except Exception as error:
        print(f"Chat error: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Chat service unavailable",
                "message": "Sorry, I'm having trouble responding right now. Please try again later."
            }
        )


@router.get("/history")
async def get_chat_history(current_user: dict = Depends(verify_token)):
    """Fetch chat history for the user (to be implemented with database)"""
    return {
        "message": "Chat history endpoint - to be implemented with the database",
        "userId": current_user['userId']
    }


@router.get("/llm-status")
async def get_llm_status(current_user: dict = Depends(verify_token)):
    """Get LLM service status and available models"""
    
    is_available = llm_service.is_available()
    available_models = llm_service.get_available_models() if is_available else []
    
    return {
        "service": "OpenAI",
        "llm_available": is_available,
        "current_model": llm_service.model_name,
        "available_models": available_models,
        "api_key_configured": bool(llm_service.api_key),
        "status": "online" if is_available else "offline",
        "message": "OpenAI API is available" if is_available else "OpenAI API is not available - using fallback responses",
        "fallback_enabled": True
    }


@router.get("/rag-status")
async def get_rag_status(current_user: dict = Depends(verify_token)):
    """Get RAG system status and knowledge base statistics"""
    from app.services.rag_service import rag_service
    
    return {
        "rag_system": "active",
        "knowledge_base_stats": rag_service.get_stats(),
        "llm_integration": llm_service.get_rag_stats(),
        "retrieval_available": True,
        "message": "RAG system is operational with ISTQB knowledge base"
    }


@router.post("/search-knowledge")
async def search_knowledge(query: str, current_user: dict = Depends(verify_token)):
    """Search the knowledge base directly (for testing RAG retrieval)"""
    from app.services.rag_service import rag_service
    
    # Retrieve relevant content
    relevant_content = rag_service.retrieve_relevant_content(query, top_k=5)
    
    # Get context for LLM
    llm_context = rag_service.get_context_for_llm(query)
    
    return {
        "query": query,
        "relevant_content": relevant_content,
        "llm_context": llm_context,
        "total_results": len(relevant_content),
        "message": f"Found {len(relevant_content)} relevant entries in knowledge base"
    }


@router.get("/knowledge-stats")
async def get_knowledge_stats(current_user: dict = Depends(verify_token)):
    """Get detailed knowledge base statistics"""
    from app.services.rag_service import rag_service
    from app.services.simple_vector_store import vector_store
    
    stats = rag_service.get_stats()
    vector_stats = vector_store.get_stats()
    
    # Get categories breakdown
    categories = {}
    for faq in rag_service.knowledge_base.get("faq", []):
        category = faq.get("category", "uncategorized")
        categories[category] = categories.get(category, 0) + 1
    
    return {
        "knowledge_base_stats": stats,
        "vector_store_stats": vector_stats,
        "categories_breakdown": categories,
        "total_keywords": sum(len(faq.get("keywords", [])) for faq in rag_service.knowledge_base.get("faq", [])),
        "message": "Knowledge base statistics retrieved successfully"
    }


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), current_user: dict = Depends(verify_token)):
    """Upload and process a PDF file to add to the knowledge base"""
    from app.services.rag_service import rag_service
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Read and write file content
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the PDF
            results = rag_service.ingest_pdfs([temp_file_path])
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            if results["processed_files"]:
                return {
                    "success": True,
                    "message": f"Successfully processed PDF: {file.filename}",
                    "filename": file.filename,
                    "processed_files": results["processed_files"],
                    "errors": results["errors"]
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to process PDF: {file.filename}",
                    "filename": file.filename,
                    "errors": results["errors"]
                }
                
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.post("/upload-multiple-pdfs")
async def upload_multiple_pdfs(files: List[UploadFile] = File(...), current_user: dict = Depends(verify_token)):
    """Upload and process multiple PDF files"""
    from app.services.rag_service import rag_service
    
    # Validate all files are PDFs
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is not a PDF. Only PDF files are supported."
            )
    
    temp_files = []
    results = {
        "processed_files": [],
        "errors": [],
        "total_files": len(files)
    }
    
    try:
        # Save all files to temporary locations
        for file in files:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_files.append((temp_file.name, file.filename))
        
        # Process all PDFs
        pdf_paths = [temp_path for temp_path, _ in temp_files]
        processing_results = rag_service.ingest_pdfs(pdf_paths)
        
        # Map results back to original filenames
        for temp_path, original_name in temp_files:
            if temp_path in processing_results["processed_files"]:
                results["processed_files"].append(original_name)
        
        # Map errors to original filenames
        for error in processing_results["errors"]:
            original_name = next(
                (orig for temp, orig in temp_files if temp == error["file"]),
                error["file"]
            )
            results["errors"].append({
                "file": original_name,
                "error": error["error"]
            })
        
        return {
            "success": len(results["processed_files"]) > 0,
            "message": f"Processed {len(results['processed_files'])} out of {len(files)} PDF files",
            "results": results
        }
        
    finally:
        # Clean up all temporary files
        for temp_path, _ in temp_files:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


@router.get("/vector-store-stats")
async def get_vector_store_stats(current_user: dict = Depends(verify_token)):
    """Get detailed vector store statistics"""
    from app.services.simple_vector_store import vector_store
    
    return {
        "vector_store_stats": vector_store.get_stats(),
        "message": "Vector store statistics retrieved successfully"
    }


@router.post("/clear-vector-store")
async def clear_vector_store(current_user: dict = Depends(verify_token)):
    """Clear all documents from the vector store (admin function)"""
    from app.services.simple_vector_store import vector_store
    
    try:
        success = vector_store.clear_all()
        if success:
            vector_store.save_vector_store()
            return {
                "success": True,
                "message": "Vector store cleared successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to clear vector store"
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing vector store: {str(e)}"
        )


@router.post("/upload-massive-pdf")
async def upload_massive_pdf(file: UploadFile = File(...), current_user: dict = Depends(verify_token)):
    """Upload and process massive PDF files with streaming and progress tracking"""
    from app.services.enhanced_pdf_processor import enhanced_pdf_processor
    from app.services.simple_vector_store import vector_store
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    temp_file_path = None
    try:
        # Read file size from content
        content = await file.read()
        file_size = len(content)
        
        # Check if file is too large (100MB limit)
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large: {file_size / (1024*1024):.1f}MB (max: {max_size / (1024*1024):.1f}MB)"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Get memory usage estimate
        memory_estimate = enhanced_pdf_processor.get_memory_usage_estimate(file_size)
        
        # Process the massive PDF with enhanced processor
        processing_result = await enhanced_pdf_processor.process_massive_pdf(
            temp_file_path,
            source_info={
                "uploaded_by": current_user['userId'],
                "original_filename": file.filename,
                "upload_timestamp": datetime.now().isoformat()
            }
        )
        
        if not processing_result.get("success", False):
            return {
                "success": False,
                "message": f"Failed to process massive PDF: {file.filename}",
                "filename": file.filename,
                "error": processing_result.get("error", "Unknown error"),
                "file_info": processing_result.get("file_info", {})
            }
        
        # Add chunks to vector store in batches to manage memory
        chunks = processing_result["chunks"]
        batch_size = 100  # Process 100 chunks at a time
        total_added = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            document_ids = vector_store.add_documents(batch)
            total_added += len(document_ids)
        
        # Save vector store updates
        vector_store.save_vector_store()
        
        return {
            "success": True,
            "message": f"Successfully processed massive PDF: {file.filename}",
            "filename": file.filename,
            "file_info": processing_result["file_info"],
            "processing_stats": {
                "total_pages": processing_result["source_metadata"].get("total_pages", 0),
                "total_chunks": processing_result["total_chunks"],
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "processing_method": "enhanced_streaming"
            },
            "memory_estimate": memory_estimate,
            "chunks_added": total_added
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing massive PDF: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.get("/pdf-upload-limits")
async def get_pdf_upload_limits(current_user: dict = Depends(verify_token)):
    """Get information about PDF upload limits and capabilities"""
    return {
        "standard_upload": {
            "max_file_size_mb": 50,
            "endpoint": "/api/chat/upload-pdf",
            "description": "Standard PDF upload for smaller files"
        },
        "massive_upload": {
            "max_file_size_mb": 100,
            "endpoint": "/api/chat/upload-massive-pdf",
            "description": "Enhanced upload for massive PDF files with streaming processing",
            "features": [
                "Memory-efficient streaming processing",
                "Batch processing to handle large files",
                "Progress tracking",
                "Advanced text chunking"
            ]
        },
        "recommendations": {
            "small_files": "Use /upload-pdf for files under 10MB",
            "large_files": "Use /upload-massive-pdf for files over 10MB",
            "very_large_files": "Files over 50MB will use enhanced streaming processing"
        }
    }


# Chatbot response generator

def generate_chatbot_response(message: str) -> dict:
    """ISTQB Certification Guidance Chatbot Response Generator"""
    from app.data.istqb_certifications import certifications, training_providers, career_paths
    
    lower_message = message.lower().strip()

    # Certification recommendation patterns
    if any(phrase in lower_message for phrase in ['which certification', 'what certification', 'start with', 'recommend']):
        return {
            'intent': 'certification_recommendation',
            'message': '🎯 I\'d be happy to recommend the right ISTQB certification for you! To give you the best advice, could you tell me:\n\n• What\'s your current experience level in testing?\n• What\'s your current role?\n• What are your career goals?\n\nFor most beginners, I typically recommend starting with the **CTFL (Foundation Level)** as it provides essential testing fundamentals.',
            'suggestions': ['I\'m new to testing', 'I have 2+ years experience', 'I want to be a test manager', 'Tell me about Foundation Level']
        }

    # Foundation Level specific queries
    if any(phrase in lower_message for phrase in ['foundation', 'ctfl', 'beginner', 'new to testing']):
        ctfl = certifications['CTFL']
        return {
            'intent': 'foundation_level_info',
            'message': f'📚 **CTFL (Foundation Level)** is perfect for you!\n\n**What it covers:**\n• {", ".join(ctfl["topics"][:3])}\n\n**Exam Details:**\n• {ctfl["examFormat"]["questions"]} questions in {ctfl["examFormat"]["duration"]}\n• {ctfl["examFormat"]["passingScore"]} to pass\n\n**Study Time:** {ctfl["estimatedStudyTime"]}\n**Cost:** {ctfl["averageCost"]}\n\n{ctfl["careerValue"]}',
            'suggestions': ['Find training courses', 'Advanced certifications', 'Study materials', 'Exam registration']
        }

    # Advanced Level queries
    if any(phrase in lower_message for phrase in ['advanced', 'ctal', 'next level']):
        return {
            'intent': 'advanced_level_info',
            'message': '🚀 **Advanced Level Certifications** - Great for career growth!\n\nChoose based on your career path:\n\n**🔬 CTAL-TA (Test Analyst)**\n• For technical testing specialists\n• Deep dive into test techniques\n• 180-minute exam with 65 questions\n\n**👥 CTAL-TM (Test Manager)**\n• For team leaders and managers\n• Focus on test management skills\n• Leadership and strategy emphasis\n\n**🤖 CTAL-TAE (Test Automation Engineering)**\n• For automation specialists\n• High-demand technical skills\n• Perfect for DevOps environments\n\n*All require CTFL certification first*',
            'suggestions': ['Tell me about Test Analyst', 'I want to be a manager', 'Automation interests me', 'Prerequisites info']
        }

    # Training and course queries
    if any(phrase in lower_message for phrase in ['training', 'course', 'study', 'where to learn']):
        return {
            'intent': 'training_providers',
            'message': '📖 **Training Options for ISTQB Certifications:**\n\n**Official Sources:**\n• ASTQB (astqb.org) - Official US board\n• ISTQB Partner Network - Accredited providers worldwide\n\n**Online Platforms:**\n• **Udemy** - $50-200, self-paced courses\n• **Coursera** - $39-79/month, university partnerships\n• **Pluralsight** - $45/month, tech-focused\n\n**Formats Available:**\n• Self-paced online learning\n• Instructor-led virtual classes\n• In-person workshops\n• Blended learning programs\n\nWhich certification are you interested in training for?',
            'suggestions': ['CTFL training', 'Advanced level courses', 'Online vs in-person', 'Cost comparison']
        }

    # Experience-based advice
    if any(phrase in lower_message for phrase in ['experience', 'years', 'background']):
        return {
            'intent': 'experience_based_advice',
            'message': '💼 **Experience-Based Recommendations:**\n\n**👶 0-2 years (New to Testing):**\n• Start with CTFL Foundation Level\n• Build fundamental knowledge first\n\n**🔧 2-5 years (Test Analyst Track):**\n• CTFL → CTAL-TA\n• Consider specialist certifications (Mobile, AI)\n\n**👑 3-7 years (Management Track):**\n• CTFL → CTAL-TM\n• Focus on leadership skills\n\n**🤖 2-6 years (Automation Track):**\n• CTFL → CTAL-TAE\n• High demand in DevOps environments\n\n**🎯 5+ years (Senior Specialist):**\n• Combine Advanced + Specialist certifications\n• Consider CT-AI, CT-MAT, or domain-specific certs\n\nWhat\'s your current experience level?',
            'suggestions': ['I have 1 year experience', 'I have 5+ years', 'I work in automation', 'I want to manage teams']
        }

    # Specialist certification queries
    if any(phrase in lower_message for phrase in ['specialist', 'mobile', 'ai', 'automotive']):
        return {
            'intent': 'specialist_certifications',
            'message': '🎯 **Specialist ISTQB Certifications:**\n\n**📱 CT-MAT (Mobile Application Testing)**\n• Perfect for mobile app testers\n• High demand specialization\n• 90-minute exam, 40 questions\n\n**🤖 CT-AI (AI Testing)**\n• Cutting-edge AI/ML testing\n• Future-proof specialization\n• Growing market demand\n\n**🚗 CT-AuT (Automotive Software Testing)**\n• Automotive industry focus\n• Safety and security emphasis\n• Embedded systems expertise\n\nAll require CTFL certification first. Which area interests you most?',
            'suggestions': ['Mobile testing details', 'AI testing info', 'Automotive testing', 'Tell me about CTFL first']
        }

    # Career and salary queries
    if any(phrase in lower_message for phrase in ['career', 'salary', 'job', 'worth it']):
        return {
            'intent': 'career_advice',
            'message': '💰 **ISTQB Career Value & Impact:**\n\n**Foundation Level (CTFL):**\n• Entry-level boost: 10-20% salary increase\n• Opens doors to testing roles globally\n• Essential for career progression\n\n**Advanced Level:**\n• Senior roles: 20-40% salary increase\n• Leadership opportunities\n• Technical specialist positions\n\n**Specialist Certifications:**\n• Niche expertise premium\n• Competitive advantage\n• Higher hourly rates for consultants\n\n**Market Demand (2024):**\n• Automation (CTAL-TAE) - Very High\n• AI Testing (CT-AI) - Rapidly Growing\n• Mobile (CT-MAT) - Consistently High\n• Test Management (CTAL-TM) - Stable Demand\n\nROI typically pays back within 6-12 months!',
            'suggestions': ['Salary expectations', 'Best ROI certifications', 'Job market trends', 'Remote work impact']
        }

    # Greeting patterns
    if any(phrase in lower_message for phrase in ['hello', 'hi', 'hey']):
        return {
            'intent': 'greeting',
            'message': '👋 Hello! I\'m your ISTQB certification guidance assistant. I can help you with:\n\n🎯 **Certification Recommendations** - Find the right cert for your experience\n📚 **Training Providers** - Connect you with quality courses\n💼 **Career Advice** - Understand the value and career impact\n📋 **Requirements & Prerequisites** - Plan your certification journey\n\nWhat would you like to know about ISTQB certifications?',
            'suggestions': ['Which certification should I start with?', 'Find training courses', 'Career benefits', 'Help me choose']
        }

    # Help patterns
    if any(phrase in lower_message for phrase in ['help', 'what can you do']):
        return {
            'intent': 'help',
            'message': '🤖 **I\'m your ISTQB Certification Expert!** Here\'s how I can help:\n\n🎯 **Certification Guidance:**\n• Recommend the right certification for your experience\n• Explain prerequisites and requirements\n• Compare different certification paths\n\n📚 **Training & Courses:**\n• Find accredited training providers\n• Compare online vs in-person options\n• Estimate costs and study time\n\n💼 **Career Advice:**\n• Understand certification value and ROI\n• Career path recommendations\n• Salary impact and job market insights\n\n📋 **Exam Preparation:**\n• Study strategies and timelines\n• Exam format and structure\n• Success tips from certified professionals\n\nJust ask me anything about ISTQB certifications!',
            'suggestions': ['Recommend a certification', 'Find training courses', 'Career impact', 'Exam requirements']
        }

    # Default response
    return {
        'intent': 'unknown',
        'message': '🤔 I\'m not sure I understand that specific question, but I\'m here to help with ISTQB certifications! I can assist you with:\n\n🎯 **Certification Selection** - Which cert is right for you?\n📚 **Training Resources** - Where to find quality courses\n💼 **Career Guidance** - How certifications impact your career\n📋 **Requirements** - Prerequisites and exam details\n\nTry asking me something like:\n• "Which ISTQB certification should I start with?"\n• "Where can I find training for CTFL?"\n• "What\'s the career value of Advanced Level?"',
        'suggestions': ['Which certification for beginners?', 'Find training courses', 'Career benefits', 'Help me choose']
    }
