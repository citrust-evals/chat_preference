# LLM Evaluation API

A FastAPI application for collecting and storing LLM evaluation feedback in MongoDB.

## Features

- ✅ FastAPI endpoint for submitting evaluation data
- ✅ MongoDB integration for data persistence
- ✅ Pydantic validation for data integrity
- ✅ Automatic API documentation (Swagger UI)
- ✅ Health check endpoint
- ✅ Statistics endpoint
- ✅ CORS support

## Installation

1. Install dependencies:
```powershell
pip install -r requirements.txt
```

2. (Optional) Create a `.env` file based on `.env.example` if you want to customize settings.

## Running the Application

Start the server:
```powershell
python app.py
```

Or use uvicorn directly:
```powershell
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### POST /api/v1/evaluation
Submit LLM evaluation feedback

**Request Body:**
```json
{
  "chat_history": [
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing well, thank you!"}
  ],
  "exact_turn": "I'm doing well, thank you!",
  "thumbs": "up",
  "user_id": "user_123",
  "session_id": "session_456",
  "chat_id": "chat_789",
  "chat_created_at": "2025-11-12T10:30:00Z",
  "thumbs_created_at": "2025-11-12T10:31:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Evaluation feedback saved successfully",
  "evaluation_id": "507f1f77bcf86cd799439011",
  "timestamp": "2025-11-12T10:31:05.123456"
}
```

### GET /health
Health check endpoint

### GET /api/v1/stats
Get basic statistics about stored evaluations

### GET /
Root endpoint with API information

## Data Model

### EvaluationRequest
- `chat_history`: List of chat messages (role, content)
- `exact_turn`: The specific turn being evaluated
- `thumbs`: "up" or "down"
- `user_id`: User identifier
- `session_id`: Session identifier
- `chat_id`: Chat identifier
- `chat_created_at`: Chat creation timestamp
- `thumbs_created_at`: Feedback timestamp

## MongoDB Setup

The application connects to MongoDB using the connection string in `config.py`:
- **Database**: citrust
- **Collection**: evaluations

Data is automatically stored with ISO-formatted timestamps.

## Testing with curl

```powershell
curl -X POST "http://localhost:8000/api/v1/evaluation" `
  -H "Content-Type: application/json" `
  -d '{
    "chat_history": [{"role": "user", "content": "Hello"}],
    "exact_turn": "Hello",
    "thumbs": "up",
    "user_id": "user_123",
    "session_id": "session_456",
    "chat_id": "chat_789",
    "chat_created_at": "2025-11-12T10:30:00Z",
    "thumbs_created_at": "2025-11-12T10:31:00Z"
  }'
```

## Development

The application includes:
- Automatic request validation
- Error handling and logging
- CORS middleware for cross-origin requests
- Connection pooling for MongoDB
- Proper startup/shutdown lifecycle management

## License

MIT
