"""
FastAPI application for LLM Evaluation - UPDATED
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import MultiResponseRequest, MultiResponseResponse, FeedbackRequest, EvaluationResponse
from database import mongodb
from config import settings
import logging
from datetime import datetime
import uuid
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini
genai.configure(api_key=settings.gemini_api_key)

# In-memory storage for chat sessions (production mein Redis ya database use karna)
chat_sessions = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("Starting up LLM Evaluation API...")
    mongodb.connect()
    yield
    # Shutdown
    logger.info("Shutting down LLM Evaluation API...")
    mongodb.close()


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Complete API for LLM multi-response generation and evaluation",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to LLM Evaluation API",
        "version": settings.app_version,
        "endpoints": {
            "generate_responses": "/api/v1/generate-responses",
            "submit_feedback": "/api/v1/feedback",
            "health": "/health",
            "stats": "/api/v1/stats",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        mongodb.client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


@app.post(
    "/api/v1/generate-responses",
    response_model=MultiResponseResponse,
    tags=["Generation"]
)
async def generate_responses(request: MultiResponseRequest):
    """
    Generate multiple responses using Google Gemini
    Returns responses that user can choose from
    """
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        responses = []
        
        # Generate multiple responses with different temperatures
        generation_configs = [
            {"temperature": 0.3},  # More deterministic
            {"temperature": 0.7},  # Balanced
            {"temperature": 0.9}   # More creative
        ]
        
        for i, config in enumerate(generation_configs[:request.num_responses]):
            try:
                response = model.generate_content(
                    request.user_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=config["temperature"],
                        max_output_tokens=500
                    )
                )
                responses.append(response.text)
                logger.info(f"Generated response {i+1} with temperature {config['temperature']}")
                
            except Exception as e:
                logger.error(f"Error generating response {i+1}: {e}")
                # Fallback response
                responses.append(f"Response {i+1}: This is a sample response for '{request.user_prompt}'")
        
        # Generate unique chat ID
        chat_id = str(uuid.uuid4())
        
        # Store the session data for feedback
        chat_sessions[chat_id] = {
            "user_prompt": request.user_prompt,
            "responses": responses,
            "model_used": request.model_used,
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Generated {len(responses)} responses for user prompt: {request.user_prompt[:50]}...")
        
        return MultiResponseResponse(
            success=True,
            message=f"Successfully generated {len(responses)} responses using Gemini",
            user_prompt=request.user_prompt,
            responses=responses,
            chat_id=chat_id
        )
        
    except Exception as e:
        logger.error(f"Error in generate_responses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate responses: {str(e)}"
        )


@app.post(
    "/api/v1/feedback",
    response_model=EvaluationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Evaluation"]
)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback when user selects a preferred response
    
    This is called when user clicks "I prefer this response" on any response
    """
    try:
        # Get the original chat session data
        chat_data = chat_sessions.get(feedback.chat_id)
        if not chat_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found or expired"
            )
        
        # Prepare evaluation data for MongoDB
        evaluation_data = {
            # Original prompt and responses
            "user_prompt": chat_data["user_prompt"],
            "all_responses": chat_data["responses"],
            "selected_response_index": feedback.selected_response_index,
            "selected_response_text": feedback.selected_response_text,
            
            # User feedback
            "thumbs": feedback.thumbs,
            "feedback_text": feedback.feedback_text,
            
            # Metadata
            "user_id": feedback.user_id,
            "session_id": feedback.session_id,
            "chat_id": feedback.chat_id,
            "model_used": chat_data["model_used"],
            
            # Timestamps
            "prompt_created_at": chat_data["created_at"],
            "responses_created_at": chat_data["created_at"],
            "feedback_created_at": datetime.utcnow().isoformat(),
            "server_received_at": datetime.utcnow().isoformat(),
            
            # Calculated fields
            "total_responses_shown": len(chat_data["responses"])
        }
        
        # Insert into MongoDB
        evaluation_id = mongodb.insert_evaluation(evaluation_data)
        
        # Clean up session data (optional)
        # del chat_sessions[feedback.chat_id]
        
        logger.info(f"User {feedback.user_id} selected response {feedback.selected_response_index} with {feedback.thumbs} rating")
        
        return EvaluationResponse(
            success=True,
            message="Feedback submitted successfully",
            evaluation_id=evaluation_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save feedback: {str(e)}"
        )


@app.get("/api/v1/stats", tags=["Statistics"])
async def get_stats():
    """
    Get basic statistics about stored evaluations
    """
    try:
        total_evaluations = mongodb.collection.count_documents({})
        thumbs_up = mongodb.collection.count_documents({"thumbs": "up"})
        thumbs_down = mongodb.collection.count_documents({"thumbs": "down"})
        
        # Additional stats
        unique_users = len(mongodb.collection.distinct("user_id"))
        unique_sessions = len(mongodb.collection.distinct("session_id"))
        
        return {
            "total_evaluations": total_evaluations,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "positive_rate": round((thumbs_up / total_evaluations * 100), 2) if total_evaluations > 0 else 0,
            "unique_users": unique_users,
            "unique_sessions": unique_sessions
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )