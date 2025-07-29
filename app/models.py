from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# Auth Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    createdAt: Optional[str] = None


class AuthResponse(BaseModel):
    message: str
    user: UserResponse
    token: str


# Chat Models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    sessionId: Optional[str] = None


class ChatResponse(BaseModel):
    sessionId: str
    message: str
    intent: str
    suggestions: List[str] = []
    timestamp: str
    source: Optional[str] = None
    tokens_used: Optional[int] = None
    retrieved_content: Optional[List[str]] = []
    rag_context_used: Optional[bool] = None


# Certification Models
class ExamFormat(BaseModel):
    questions: int
    duration: str
    passingScore: str
    type: str


class Certification(BaseModel):
    id: str
    name: str
    level: str
    type: str
    description: str
    prerequisites: List[str]
    experienceRequired: str
    examFormat: ExamFormat
    targetAudience: List[str]
    topics: List[str]
    careerValue: str
    estimatedStudyTime: str
    averageCost: str


class CertificationRecommendation(BaseModel):
    certification: Certification
    reason: str
    priority: str


class TrainingProvider(BaseModel):
    id: str
    name: str
    website: str
    type: str
    description: str
    coursesOffered: List[str]
    formats: List[str]
    regions: List[str]
    priceRange: Optional[str] = None


# Response Models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime: Optional[float] = None


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[List[Dict[str, Any]]] = None
