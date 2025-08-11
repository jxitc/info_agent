# Info Agent - RESTful API Specification

## Overview

This document defines the RESTful API endpoints for Info Agent, providing web access to all CLI functionality through HTTP endpoints.

## Design Principles

- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Responses**: All responses in JSON format
- **CLI Parity**: Direct mapping to existing CLI commands
- **Simple & Clean**: Minimal complexity for MVP
- **Error Handling**: Consistent error response format

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

**MVP**: No authentication required
**Future**: API key or JWT token authentication

## API Endpoints

### 1. Memory Operations

#### GET /memories
**Purpose**: List recent memories (maps to `list` command)

**Parameters**:
- `limit` (optional, integer): Number of memories to return (default: 20, max: 100)
- `offset` (optional, integer): Number of memories to skip (default: 0)

**Response**:
```json
{
  "success": true,
  "data": {
    "memories": [
      {
        "id": 1,
        "title": "Meeting with Sarah about project timeline",
        "content": "Meeting with Sarah about the project timeline...",
        "word_count": 8,
        "created_at": "2024-08-10T16:11:23Z",
        "updated_at": "2024-08-10T16:11:23Z",
        "dynamic_fields": {
          "category": "work",
          "ai_processed": true
        }
      }
    ],
    "total": 50,
    "has_more": true
  }
}
```

#### GET /memories/{id}
**Purpose**: Get specific memory details (maps to `show` command)

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Meeting with Sarah about project timeline",
    "content": "Meeting with Sarah about the project timeline...",
    "word_count": 8,
    "content_hash": "a1b2c3d4e5f6g7h8...",
    "version": 1,
    "created_at": "2024-08-10T16:11:23Z",
    "updated_at": "2024-08-10T16:11:23Z",
    "dynamic_fields": {
      "category": "work",
      "people": ["Sarah"],
      "ai_processed": true,
      "ai_model": "gpt-3.5-turbo"
    }
  }
}
```

#### POST /memories
**Purpose**: Create new memory (maps to `add` command)

**Request Body**:
```json
{
  "content": "Meeting with Sarah about project timeline",
  "title": "Custom Title" // optional
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 13,
    "title": "Meeting with Sarah about project timeline",
    "content": "Meeting with Sarah about project timeline",
    "word_count": 8,
    "created_at": "2024-08-10T16:11:23Z",
    "dynamic_fields": {
      "ai_processed": true,
      "category": "work"
    }
  },
  "message": "Memory created successfully"
}
```

#### DELETE /memories/{id}
**Purpose**: Delete memory (maps to `delete` command)

**Response**:
```json
{
  "success": true,
  "message": "Memory deleted successfully",
  "data": {
    "deleted_id": 1,
    "title": "Meeting with Sarah about project timeline"
  }
}
```

### 2. Search Operations

#### GET /search
**Purpose**: Search memories (maps to `search` command)

**Parameters**:
- `q` (required, string): Search query
- `limit` (optional, integer): Max results (default: 10, max: 50)

**Response**:
```json
{
  "success": true,
  "data": {
    "query": "integration testing",
    "results": [
      {
        "memory_id": 13,
        "title": "Test memory for integration testing",
        "snippet": "Test memory for integration testing...",
        "relevance_score": 0.676,
        "match_type": "hybrid"
      }
    ],
    "total_found": 7,
    "search_time_ms": 45
  }
}
```

### 3. System Operations

#### GET /status
**Purpose**: Get system status (maps to `status` command)

**Response**:
```json
{
  "success": true,
  "data": {
    "version": "0.1.0",
    "python_version": "3.9.6",
    "services": {
      "database": {
        "status": "connected",
        "total_memories": 15,
        "database_size_mb": 0.1
      },
      "vector_store": {
        "status": "available",
        "document_count": 6
      },
      "ai_services": {
        "status": "available",
        "model": "gpt-3.5-turbo"
      }
    }
  }
}
```

### 4. Testing Operations (Development)

#### POST /test/llm
**Purpose**: Test LLM extraction (maps to `llm extract` command)

**Request Body**:
```json
{
  "text": "Meeting with Sarah tomorrow at 2pm",
  "save": false
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "extracted": {
      "title": "Meeting with Sarah Tomorrow",
      "categories": ["work", "meetings"],
      "people": ["Sarah"],
      "dates_times": ["tomorrow at 2pm"]
    },
    "tokens_used": 142,
    "model": "gpt-3.5-turbo"
  }
}
```

## Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": {
    "code": "MEMORY_NOT_FOUND",
    "message": "Memory with ID 999 not found",
    "details": {}
  }
}
```

### HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: AI services unavailable

### Error Codes
- `MEMORY_NOT_FOUND`: Memory ID doesn't exist
- `INVALID_PARAMETER`: Invalid request parameter
- `VALIDATION_ERROR`: Request validation failed
- `AI_SERVICE_ERROR`: AI processing failed
- `DATABASE_ERROR`: Database operation failed
- `SEARCH_ERROR`: Search operation failed

## Request/Response Examples

### Create Memory with Error
**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"content": ""}'
```

**Response** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Content cannot be empty",
    "details": {
      "field": "content",
      "constraint": "min_length"
    }
  }
}
```

### Search with No Results
**Request**:
```bash
curl "http://localhost:8000/api/v1/search?q=nonexistent"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "query": "nonexistent",
    "results": [],
    "total_found": 0,
    "search_time_ms": 12
  }
}
```

## Implementation Notes

### Flask Structure
```
api/
├── __init__.py
├── app.py               # Flask app factory
├── routes/
│   ├── __init__.py
│   ├── memories.py      # Memory CRUD endpoints
│   ├── search.py        # Search endpoints
│   └── system.py        # System status endpoints
├── utils/
│   ├── __init__.py
│   ├── responses.py     # JSON response helpers
│   ├── validation.py    # Request validation
│   └── errors.py        # Error handling
└── config.py            # Flask configuration
```

### Response Helpers (Flask)
```python
from flask import jsonify

def success_response(data=None, message=None):
    response = {"success": True}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return jsonify(response)

def error_response(code, message, details=None, status=400):
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }
    return jsonify(response), status
```

**Key Integration Points:**
- **Reuse existing services**: API calls same MemoryService used by CLI
- **Error mapping**: Convert RepositoryError/ProcessingError to HTTP errors
- **Response formatting**: Transform CLI output to JSON responses

## Development Priority

### Phase 1 (MVP)
1. Flask app structure with blueprints
2. Memory CRUD endpoints (GET, POST, DELETE)
3. Basic search endpoint
4. System status endpoint
5. JSON response helpers and error handling
6. Basic request validation

### Phase 2 (Enhancement)
7. CORS support for web integration
8. Request/response logging
9. Input sanitization and security
10. Basic API documentation
11. Performance optimization

### Phase 3 (Production)
12. Authentication and authorization (Flask-Login or JWT)
13. Rate limiting (Flask-Limiter)
14. Caching layer (Flask-Caching)
15. Health checks and monitoring

## Flask Dependencies

### Required Packages
```bash
pip install flask flask-cors
```

### Optional Enhancement Packages
```bash
pip install flask-limiter flask-caching flask-login
```

---

*This API specification provides the foundation for creating a web-friendly interface to all Info Agent functionality while maintaining simplicity and direct CLI command mapping.*
