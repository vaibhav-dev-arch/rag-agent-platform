# API Documentation

Complete API reference for the RAG Agent Platform.

## 🚀 Getting Started

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### Authentication
Currently, the API does not require authentication. Future versions will include API key authentication.

## 📚 Endpoints

### 1. Health Check

#### GET `/health`
Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### 2. Query Processing

#### POST `/query`
Process a query using the RAG system.

**Request Body:**
```json
{
  "query": "What is RAG?",
  "context": "optional context",
  "max_tokens": 500,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "query": "What is RAG?",
  "response": "RAG (Retrieval-Augmented Generation) is a technique that combines...",
  "sources": [
    {
      "title": "RAG System Documentation",
      "url": "https://example.com/rag-docs",
      "relevance_score": 0.95
    }
  ],
  "processing_time": 1.23,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST `/query/stream`
Stream query processing results.

**Request Body:**
```json
{
  "query": "Explain RAG in detail",
  "stream": true
}
```

**Response:** Server-Sent Events (SSE) stream

### 3. Document Management

#### POST `/documents/upload`
Upload documents for indexing.

**Request:** Multipart form data
- `file`: Document file (PDF, TXT, DOCX, etc.)
- `title`: Document title (optional)
- `description`: Document description (optional)

**Response:**
```json
{
  "document_id": "doc_123456",
  "title": "RAG System Guide",
  "status": "uploaded",
  "processing_status": "indexing",
  "upload_time": "2024-01-01T12:00:00Z"
}
```

#### GET `/documents`
List all uploaded documents.

**Query Parameters:**
- `limit`: Number of documents to return (default: 10)
- `offset`: Number of documents to skip (default: 0)
- `status`: Filter by status (uploaded, indexed, error)

**Response:**
```json
{
  "documents": [
    {
      "document_id": "doc_123456",
      "title": "RAG System Guide",
      "status": "indexed",
      "upload_time": "2024-01-01T12:00:00Z",
      "size": 1024000
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### GET `/documents/{document_id}`
Get document details.

**Response:**
```json
{
  "document_id": "doc_123456",
  "title": "RAG System Guide",
  "description": "Comprehensive guide to RAG systems",
  "status": "indexed",
  "upload_time": "2024-01-01T12:00:00Z",
  "indexing_time": "2024-01-01T12:05:00Z",
  "size": 1024000,
  "chunks": 150
}
```

#### DELETE `/documents/{document_id}`
Delete a document.

**Response:**
```json
{
  "document_id": "doc_123456",
  "status": "deleted",
  "deleted_at": "2024-01-01T12:00:00Z"
}
```

### 4. Agent Operations

#### POST `/agents/create`
Create a new agent.

**Request Body:**
```json
{
  "name": "Research Agent",
  "description": "Agent for research tasks",
  "capabilities": ["web_search", "document_analysis"],
  "model": "gpt-3.5-turbo",
  "temperature": 0.7
}
```

**Response:**
```json
{
  "agent_id": "agent_789012",
  "name": "Research Agent",
  "status": "created",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### POST `/agents/{agent_id}/execute`
Execute a task with an agent.

**Request Body:**
```json
{
  "task": "Research the latest developments in RAG",
  "parameters": {
    "max_sources": 5,
    "depth": "comprehensive"
  }
}
```

**Response:**
```json
{
  "task_id": "task_345678",
  "status": "completed",
  "result": "Based on recent research...",
  "execution_time": 15.67,
  "sources_used": 5
}
```

### 5. System Information

#### GET `/system/info`
Get system information.

**Response:**
```json
{
  "version": "1.0.0",
  "python_version": "3.11.0",
  "llamaindex_version": "0.10.20",
  "openai_version": "1.12.0",
  "system_resources": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1
  },
  "active_agents": 3,
  "indexed_documents": 25
}
```

#### GET `/system/metrics`
Get system performance metrics.

**Response:**
```json
{
  "queries_processed": 1250,
  "average_response_time": 1.23,
  "success_rate": 98.5,
  "error_rate": 1.5,
  "uptime": "7 days, 12 hours",
  "last_updated": "2024-01-01T12:00:00Z"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `API_HOST` | API server host | `0.0.0.0` | No |
| `API_PORT` | API server port | `8000` | No |
| `MAX_DOCUMENTS` | Maximum documents to index | `1000` | No |
| `MAX_QUERY_LENGTH` | Maximum query length | `1000` | No |

### Rate Limiting

- **Queries**: 100 requests per minute per IP
- **Document uploads**: 10 requests per minute per IP
- **Video generation**: 5 requests per hour per IP

## 📝 Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_QUERY",
    "message": "Query cannot be empty",
    "details": "The query parameter is required and must not be empty",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_QUERY` | 400 | Invalid query parameters |
| `QUERY_TOO_LONG` | 400 | Query exceeds maximum length |
| `DOCUMENT_NOT_FOUND` | 404 | Document not found |
| `AGENT_NOT_FOUND` | 404 | Agent not found |
| `VIDEO_NOT_FOUND` | 404 | Video not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `OPENAI_API_ERROR` | 502 | OpenAI API error |
| `INDEXING_ERROR` | 500 | Document indexing error |

## 🔐 Security

### Input Validation
- All inputs are validated and sanitized
- SQL injection protection
- XSS protection
- File upload restrictions

### Rate Limiting
- IP-based rate limiting
- User-based rate limiting (future)
- API key-based rate limiting (future)

### CORS
- Configurable CORS settings
- Default: Allow all origins (development)
- Production: Restricted origins

## 📊 Monitoring

### Health Checks
- `/health` endpoint for basic health
- `/health/detailed` for comprehensive health check
- Database connectivity checks
- External service connectivity checks

### Logging
- Structured JSON logging
- Request/response logging
- Error logging with stack traces
- Performance metrics logging

### Metrics
- Query processing time
- Success/failure rates
- Resource usage
- API usage statistics

## 🚀 Examples

### Python Client

```python
import requests

# Initialize client
base_url = "http://localhost:8000"
client = requests.Session()

# Health check
response = client.get(f"{base_url}/health")
print(response.json())

# Query processing
query_data = {
    "query": "What is RAG?",
    "max_tokens": 500
}
response = client.post(f"{base_url}/query", json=query_data)
result = response.json()
print(result["response"])

# Document upload
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"title": "My Document"}
    response = client.post(f"{base_url}/documents/upload", 
                          files=files, data=data)
    print(response.json())
```

### JavaScript Client

```javascript
// Initialize client
const baseUrl = "http://localhost:8000";

// Health check
async function healthCheck() {
    const response = await fetch(`${baseUrl}/health`);
    const data = await response.json();
    console.log(data);
}

// Query processing
async function processQuery(query) {
    const response = await fetch(`${baseUrl}/query`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query })
    });
    const result = await response.json();
    return result.response;
}

// Document upload
async function uploadDocument(file, title) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    
    const response = await fetch(`${baseUrl}/documents/upload`, {
        method: "POST",
        body: formData
    });
    return response.json();
}
```

### cURL Examples

```bash
# Health check
curl -X GET http://localhost:8000/health

# Query processing
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'

# Document upload
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@document.pdf" \
  -F "title=My Document"

# Video generation
curl -X POST http://localhost:8000/video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "My Project",
    "description": "Project description",
    "tech_stack": ["Python", "LlamaIndex"]
  }'
```

## 🔄 WebSocket API

### Connection
```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onopen = function(event) {
    console.log("WebSocket connected");
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log("Received:", data);
};
```

### Message Format
```json
{
  "type": "query",
  "data": {
    "query": "What is RAG?",
    "stream": true
  }
}
```

### Response Format
```json
{
  "type": "response",
  "data": {
    "query": "What is RAG?",
    "response": "RAG is...",
    "sources": [...]
  }
}
```

## 📈 Performance

### Benchmarks
- **Query Processing**: ~1-3 seconds average
- **Document Indexing**: ~10-30 seconds per document
- **Concurrent Users**: Up to 100 simultaneous users

### Optimization Tips
1. Use appropriate query lengths
2. Batch document uploads when possible
3. Cache frequently accessed data
4. Use streaming for long responses
5. Monitor system resources

## 🆘 Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check API key validity
   - Verify rate limits
   - Check network connectivity

2. **Document Indexing Failures**
   - Verify file format support
   - Check file size limits
   - Ensure sufficient disk space

3. **Agent Issues**
   - Verify tool configurations
   - Check memory buffer settings
   - Ensure sufficient system resources

### Debug Mode
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python -m src api
```

### Support
- **GitHub Issues**: [Report bugs](https://github.com/ragagentplatform/rag-agent-platform/issues)
- **Documentation**: [Full documentation](https://github.com/ragagentplatform/rag-agent-platform/wiki)
- **Community**: [Discussions](https://github.com/ragagentplatform/rag-agent-platform/discussions)