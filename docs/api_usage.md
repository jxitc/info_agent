# API Usage Guide - Info Agent

This guide shows how to quickly test and interact with the Info Agent RESTful API using curl commands and other HTTP clients.

## Quick Start

### 1. Start the API Server

```bash
# Activate virtual environment
source venv/bin/activate

# Install Flask dependencies (if not already installed)
pip install flask flask-cors

# Start the development server
python -m info_agent.api.app
```

The API server will start at: `http://localhost:8001`

### 2. Test Basic Connectivity

```bash
# Health check
curl http://localhost:8001/health

# Expected response:
{
  "service": "info-agent-api",
  "status": "healthy", 
  "version": "0.1.0"
}
```

## API Endpoints

All API endpoints use the base URL: `http://localhost:8001/api/v1`

### System Status

#### GET /status - System Health Check

```bash
curl http://localhost:8001/api/v1/status
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "version": "0.1.0",
    "python_version": "3.11.5",
    "platform": "Darwin",
    "overall_status": "healthy",
    "services": {
      "database": {
        "status": "connected",
        "total_memories": 15,
        "database_size_mb": 0.1
      },
      "vector_store": {
        "status": "available",
        "document_count": 6,
        "collection_name": "memories"
      },
      "ai_services": {
        "status": "available",
        "model": "gpt-3.5-turbo",
        "available_models": 12
      }
    }
  }
}
```

### Memory Operations

#### GET /memories - List Recent Memories

```bash
# List all memories (default: 20)
curl http://localhost:8001/api/v1/memories

# List with custom limit
curl "http://localhost:8001/api/v1/memories?limit=5"

# List with pagination
curl "http://localhost:8001/api/v1/memories?limit=10&offset=20"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "memories": [
      {
        "id": 1,
        "title": "Meeting with Sarah about project timeline",
        "content": "Meeting with Sarah about the project timeline",
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

#### GET /memories/{id} - Get Specific Memory

```bash
# Get memory by ID
curl http://localhost:8001/api/v1/memories/1
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Meeting with Sarah about project timeline",
    "content": "Meeting with Sarah about the project timeline",
    "word_count": 8,
    "content_hash": "a1b2c3d4e5f6g7h8...",
    "version": 1,
    "created_at": "2024-08-10T16:11:23Z",
    "updated_at": "2024-08-10T16:11:23Z",
    "dynamic_fields": {
      "category": "work",
      "people": ["Sarah"],
      "ai_processed": true
    }
  }
}
```

#### POST /memories - Create New Memory

```bash
# Create memory with AI processing
curl -X POST http://localhost:8001/api/v1/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Team meeting tomorrow at 2pm to discuss Q4 goals and budget planning"
  }'

# Create memory with custom title
curl -X POST http://localhost:8001/api/v1/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Important project deadline next Friday",
    "title": "Project Deadline Reminder"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "id": 13,
    "title": "Team Meeting Q4 Planning",
    "content": "Team meeting tomorrow at 2pm to discuss Q4 goals and budget planning",
    "word_count": 13,
    "created_at": "2024-08-11T10:30:15Z",
    "dynamic_fields": {
      "ai_processed": true,
      "category": "work",
      "people": ["team"],
      "dates_times": ["tomorrow at 2pm"]
    }
  },
  "message": "Memory created successfully"
}
```

#### DELETE /memories/{id} - Delete Memory

```bash
# Delete memory by ID
curl -X DELETE http://localhost:8001/api/v1/memories/1
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "deleted_id": 1,
    "title": "Meeting with Sarah about project timeline"
  },
  "message": "Memory deleted successfully"
}
```

### Search Operations

#### GET /search - Search Memories

```bash
# Basic search
curl "http://localhost:8001/api/v1/search?q=team+meeting"

# Search with result limit
curl "http://localhost:8001/api/v1/search?q=project+deadline&limit=5"

# Natural language search
curl "http://localhost:8001/api/v1/search?q=meetings+with+Sarah"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "query": "team meeting",
    "results": [
      {
        "memory_id": 13,
        "title": "Team Meeting Q4 Planning",
        "snippet": "Team meeting tomorrow at 2pm to discuss Q4 goals...",
        "relevance_score": 0.876,
        "match_type": "hybrid"
      },
      {
        "memory_id": 7,
        "title": "Weekly Team Standup",
        "snippet": "Regular team standup meeting notes...",
        "relevance_score": 0.654,
        "match_type": "semantic"
      }
    ],
    "total_found": 2,
    "search_time_ms": 45
  }
}
```

## Error Handling

All error responses follow this standard format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Common Error Examples

#### 404 - Memory Not Found
```bash
curl http://localhost:8001/api/v1/memories/999
```

**Response:**
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

#### 422 - Validation Error
```bash
curl -X POST http://localhost:8001/api/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"content": ""}'
```

**Response:**
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

#### 503 - AI Service Unavailable
```json
{
  "success": false,
  "error": {
    "code": "AI_SERVICE_ERROR",
    "message": "OpenAI API is currently unavailable",
    "details": {}
  }
}
```

## Testing Workflows

### Basic CRUD Workflow

1. **Check system status:**
   ```bash
   curl http://localhost:8001/api/v1/status
   ```

2. **Create a few memories:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/memories \
     -H "Content-Type: application/json" \
     -d '{"content": "Meeting with Alice about user interface design"}'
   
   curl -X POST http://localhost:8001/api/v1/memories \
     -H "Content-Type: application/json" \
     -d '{"content": "Code review session for authentication module"}'
   ```

3. **List all memories:**
   ```bash
   curl http://localhost:8001/api/v1/memories
   ```

4. **Get specific memory details:**
   ```bash
   curl http://localhost:8001/api/v1/memories/1
   ```

5. **Search for memories:**
   ```bash
   curl "http://localhost:8001/api/v1/search?q=design+meeting"
   ```

6. **Delete a memory:**
   ```bash
   curl -X DELETE http://localhost:8001/api/v1/memories/1
   ```

### Load Testing

Test with multiple concurrent requests:

```bash
# Create multiple memories in parallel
for i in {1..5}; do
  curl -X POST http://localhost:8001/api/v1/memories \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"Test memory number $i for load testing\"}" &
done
wait

# List all memories to see results
curl http://localhost:8001/api/v1/memories
```

## Using Other HTTP Clients

### HTTPie

```bash
# Install HTTPie
pip install httpie

# List memories
http GET localhost:8001/api/v1/memories

# Create memory
http POST localhost:8001/api/v1/memories \
  content="Meeting notes from product planning session"

# Search memories
http GET localhost:8001/api/v1/search q=="product planning"
```

### Python Requests

```python
import requests

# Base URL
base_url = "http://localhost:8001/api/v1"

# Create memory
response = requests.post(f"{base_url}/memories", json={
    "content": "Python API testing example"
})
print(response.json())

# Search memories
response = requests.get(f"{base_url}/search", params={
    "q": "python testing",
    "limit": 5
})
print(response.json())
```

### JavaScript/Fetch

```javascript
// Base URL
const baseUrl = 'http://localhost:8001/api/v1';

// Create memory
fetch(`${baseUrl}/memories`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    content: 'JavaScript API testing example'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Search memories
fetch(`${baseUrl}/search?q=javascript&limit=10`)
  .then(response => response.json())
  .then(data => console.log(data));
```

## Development Tips

### Enable Verbose Logging

Set Flask to debug mode for detailed request/response logging:

```bash
export FLASK_DEBUG=true
python -m info_agent.api.app
```

### CORS for Web Development

The API includes CORS support for web frontend development. All origins are allowed in development mode.

### Response Time Monitoring

Add timing to your curl commands:

```bash
curl -w "@curl-format.txt" http://localhost:8001/api/v1/memories
```

Where `curl-format.txt` contains:
```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

## Troubleshooting

### Common Issues

1. **Connection refused:**
   - Ensure API server is running: `python -m info_agent.api.app`
   - Check port 8000 is available: `lsof -i :8000`

2. **Import errors:**
   - Activate virtual environment: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

3. **Database errors:**
   - Ensure database is initialized: `python main.py status`
   - Check file permissions: `ls -la ~/.info_agent/`

4. **AI service errors:**
   - Verify OpenAI API key: `echo $OPENAI_API_KEY`
   - Test CLI first: `python main.py llm extract "test"`

### Debugging API Issues

1. **Check server logs** in the terminal running the Flask app
2. **Use verbose curl** with `-v` flag for detailed request/response info
3. **Test equivalent CLI commands** to isolate API vs service issues
4. **Check system status** endpoint for service health

---

*This API provides full programmatic access to Info Agent functionality, enabling web interfaces and integrations while maintaining feature parity with the CLI.*