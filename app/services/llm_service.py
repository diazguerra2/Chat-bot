import os
from typing import Dict, Any, Optional
from app.config import settings
from app.data.istqb_certifications import certifications, training_providers, career_paths
from .simple_openai import simple_openai
from .rag_service import rag_service


class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = "gpt-3.5-turbo"  # Using GPT-3.5-turbo for cost efficiency
        self.openai_client = simple_openai
        
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self.openai_client.is_available()
    
    def get_available_models(self) -> list:
        """Get list of available OpenAI models"""
        if self.is_available():
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        return []
    
    def generate_response(self, message: str, context: str = None) -> Dict[str, Any]:
        """Generate response using RAG with ISTQB knowledge base"""
        # Check if OpenAI is available
        is_available = self.is_available()
        
        # Retrieve relevant context from knowledge base using RAG
        rag_context = rag_service.get_context_for_llm(message)
        
        # Create comprehensive ISTQB context (combining existing + RAG)
        istqb_context = self._create_istqb_context()
        
        # Combine contexts
        full_context = f"{rag_context}\n\n{istqb_context}" if rag_context else istqb_context
        
        # Build system prompt with retrieved context
        system_prompt = f"""You are an expert ISTQB (International Software Testing Qualifications Board) certification guidance assistant. You help software testers choose the right certification path, understand exam requirements, find training providers, and advance their careers.

Relevant Knowledge Base Information:
{full_context}

Guidelines:
1. Use the relevant information above to provide accurate, helpful responses
2. Prioritize information from the knowledge base in your responses
3. If asked about non-ISTQB topics, politely redirect to ISTQB-related guidance
4. Provide specific recommendations based on user's experience level
5. Include practical advice about study time, costs, and career benefits
6. Use emojis to make responses engaging (🎯📚💼🚀)
7. Cite specific information from the knowledge base when applicable

User context: {context if context else "New conversation"}
"""
        
        try:
            # Try to use OpenAI first
            if is_available:
                return self._call_openai_with_rag(system_prompt, message, rag_context)
            else:
                # Fallback to rule-based system with RAG context
                return self._fallback_response_with_rag(message, rag_context)
                
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_response_with_rag(message, rag_context)
    
    def _call_openai(self, system_prompt: str, original_message: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": original_message}
        ]
        
        response = self.openai_client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        llm_response = response['choices'][0]['message']['content'].strip()
        
        # Determine intent from the response
        intent = self._determine_intent(original_message)
        suggestions = self._get_suggestions_for_intent(intent)
        
        return {
            "message": llm_response,
            "intent": intent,
            "suggestions": suggestions,
            "source": "openai",
            "tokens_used": response['usage']['total_tokens']
        }
    
    def _create_istqb_context(self) -> str:
        """Create comprehensive ISTQB context for the LLM"""
        context = "ISTQB Certifications Overview:\n\n"
        
        # Add certification details
        for cert_id, cert_data in certifications.items():
            context += f"**{cert_data['name']} ({cert_id})**:\n"
            context += f"- Level: {cert_data['level']}\n"
            context += f"- Prerequisites: {', '.join(cert_data['prerequisites'])}\n"
            context += f"- Study Time: {cert_data['estimatedStudyTime']}\n"
            context += f"- Cost: {cert_data['averageCost']}\n"
            context += f"- Career Value: {cert_data['careerValue']}\n"
            context += f"- Target Audience: {', '.join(cert_data['targetAudience'])}\n\n"
        
        # Add training providers
        context += "Training Providers:\n"
        for provider in training_providers:
            context += f"- {provider['name']}: {provider['description']}\n"
        
        # Add career paths
        context += "\nCareer Paths:\n"
        for path_name, path_data in career_paths.items():
            context += f"- {path_name}: {path_data['description']} (Experience: {path_data['experience']})\n"
        
        return context
    
    def _determine_intent(self, message: str) -> str:
        """Determine user intent from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['which certification', 'what certification', 'recommend', 'start with']):
            return 'certification_recommendation'
        elif any(word in message_lower for word in ['foundation', 'ctfl', 'beginner']):
            return 'foundation_level_info'
        elif any(word in message_lower for word in ['advanced', 'ctal']):
            return 'advanced_level_info'
        elif any(word in message_lower for word in ['training', 'course', 'study']):
            return 'training_providers'
        elif any(word in message_lower for word in ['career', 'salary', 'job']):
            return 'career_advice'
        elif any(word in message_lower for word in ['experience', 'years']):
            return 'experience_based_advice'
        elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return 'greeting'
        elif any(word in message_lower for word in ['help', 'what can you do']):
            return 'help'
        else:
            return 'general_inquiry'
    
    def _get_suggestions_for_intent(self, intent: str) -> list:
        """Get appropriate suggestions based on intent"""
        suggestions_map = {
            'certification_recommendation': [
                'I\'m new to testing',
                'I have 2+ years experience',
                'I want to be a test manager',
                'Tell me about Foundation Level'
            ],
            'foundation_level_info': [
                'Find training courses',
                'Advanced certifications',
                'Study materials',
                'Exam registration'
            ],
            'advanced_level_info': [
                'Tell me about Test Analyst',
                'I want to be a manager',
                'Automation interests me',
                'Prerequisites info'
            ],
            'training_providers': [
                'CTFL training',
                'Advanced level courses',
                'Online vs in-person',
                'Cost comparison'
            ],
            'career_advice': [
                'Salary expectations',
                'Best ROI certifications',
                'Job market trends',
                'Remote work impact'
            ],
            'greeting': [
                'Which certification should I start with?',
                'Find training courses',
                'Career benefits',
                'Help me choose'
            ],
            'help': [
                'Recommend a certification',
                'Find training courses',
                'Career impact',
                'Exam requirements'
            ]
        }
        
        return suggestions_map.get(intent, [
            'Which certification for beginners?',
            'Find training courses',
            'Career benefits',
            'Help me choose'
        ])
    
    def _call_openai_with_rag(self, system_prompt: str, original_message: str, rag_context: str) -> Dict[str, Any]:
        """Call OpenAI API with RAG context"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": original_message}
        ]
        
        try:
            response = self.openai_client.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=600  # Increased for more detailed responses with context
            )
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            raise
        
        llm_response = response['choices'][0]['message']['content'].strip()
        
        # Determine intent from the response
        intent = self._determine_intent(original_message)
        suggestions = self._get_suggestions_for_intent(intent)
        
        # Get relevant content that was retrieved
        retrieved_content = rag_service.retrieve_relevant_content(original_message, top_k=3)
        
        return {
            "message": llm_response,
            "intent": intent,
            "suggestions": suggestions,
            "source": "openai_with_rag",
            "tokens_used": response['usage']['total_tokens'],
            "retrieved_content": [item.get('id', 'unknown') for item in retrieved_content],
            "rag_context_used": bool(rag_context)
        }
    
    def _fallback_response_with_rag(self, message: str, rag_context: str) -> Dict[str, Any]:
        """Fallback to rule-based system with RAG context when LLM is not available"""
        # Get the original rule-based response
        from app.routes.chat import generate_chatbot_response
        base_response = generate_chatbot_response(message)
        
        # If we have RAG context, enhance the response
        if rag_context:
            # Get relevant content for additional context
            retrieved_content = rag_service.retrieve_relevant_content(message, top_k=2)
            
            if retrieved_content:
                # Add relevant information to the response
                enhanced_message = base_response["message"]
                
                # Add most relevant FAQ or doc content
                top_content = retrieved_content[0]
                if top_content["type"] == "faq":
                    enhanced_message += f"\n\n📋 **Related Information:**\n{top_content['answer']}"
                else:
                    enhanced_message += f"\n\n📚 **From ISTQB Documentation:**\n{top_content['content']}"
                
                base_response["message"] = enhanced_message
                base_response["source"] = "rule_based_with_rag"
                base_response["retrieved_content"] = [item.get('id', 'unknown') for item in retrieved_content]
                base_response["rag_context_used"] = True
            else:
                base_response["source"] = "rule_based_no_rag"
                base_response["rag_context_used"] = False
        else:
            base_response["source"] = "rule_based_no_rag"
            base_response["rag_context_used"] = False
        
        return base_response
    
    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Fallback to rule-based system when LLM is not available"""
        return self._fallback_response_with_rag(message, "")
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return {
            "rag_service_available": rag_service is not None,
            "knowledge_base_stats": rag_service.get_stats() if rag_service else {},
            "llm_available": self.is_available()
        }


# Global LLM service instance
llm_service = LLMService()
