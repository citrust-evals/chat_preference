"""
Pydantic models for data validation - UPDATED
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message in the conversation"""
    role: str
    content: str
    timestamp: datetime | None = None


class MultiResponseRequest(BaseModel):
    """Request model for generating multiple responses"""
    user_prompt: str = Field(..., description="User's original prompt/question")
    model_used: str = Field(default="gemini-2.0-flash", description="Which AI model to use")
    num_responses: int = Field(default=3, description="Number of responses to generate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_prompt": "Best laptop under 50k?",
                "model_used": "gemini-2.0-flash",
                "num_responses": 3
            }
        }


class FeedbackRequest(BaseModel):
    """Request model when user selects a preferred response"""
    chat_id: str = Field(..., description="Chat ID from generate-responses endpoint")
    selected_response_index: int = Field(..., description="Index of the selected response (0, 1, 2)")
    selected_response_text: str = Field(..., description="The actual response text user selected")
    thumbs: Literal["up", "down"] = Field(..., description="User feedback")
    feedback_text: Optional[str] = Field(None, description="Optional text feedback from user")
    user_id: str = Field(..., description="Unique identifier for the user")
    session_id: str = Field(..., description="Unique identifier for the session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chat_id": "a1b2c3d4-5678-90ef-ghij-klmnopqrstuv",
                "selected_response_index": 1,
                "selected_response_text": "HP Pavilion with Ryzen 5...",
                "thumbs": "up",
                "feedback_text": "Liked the detailed specs",
                "user_id": "user_123",
                "session_id": "session_456"
            }
        }


class MultiResponseResponse(BaseModel):
    """Response for multi-response generation"""
    success: bool
    message: str
    user_prompt: str
    responses: List[str]
    chat_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EvaluationResponse(BaseModel):
    """Response model after saving evaluation"""
    success: bool
    message: str
    evaluation_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)