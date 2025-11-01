# RAG Agent Platform

A comprehensive, production-ready RAG (Retrieval-Augmented Generation) platform with agent architecture, security hardening, and database persistence.

## 🚀 Features

### Core RAG Platform
- **RAG System**: Retrieval-Augmented Generation with vector embeddings
- **Agent Architecture**: ReActAgent for reasoning and action-taking
- **LlamaIndex Integration**: Robust document indexing and retrieval
- **OpenAI Support**: GPT-3.5-turbo for high-quality language generation
- **Web Scraping**: BeautifulSoup for information gathering
- **Local LLM Support**: Ollama integration for offline operation
- **Mock RAG**: Development and testing without API costs

### Production-Ready Features ✨ (Phase 1, 2 & 3 Complete)
- **Security**: Rate limiting, input validation, CORS configuration, JWT infrastructure
- **Database Persistence**: SQLite & PostgreSQL support with SQLAlchemy
- **Query History**: Automatic tracking of all queries and responses
- **Vector Database**: Support for Chroma, Qdrant, and Pinecone
- **Database Migrations**: Alembic for schema management
- **Comprehensive Testing**: Unit tests, integration tests, and test fixtures
- **Docker & Kubernetes**: Full containerization and orchestration support
- **Monitoring & Observability**: Prometheus metrics, Grafana dashboards, structured logging
- **Error Tracking**: Sentry integration for production error monitoring
- **Caching Layer**: Redis integration for performance optimization
- **Auto-Scaling**: Kubernetes HPA for automatic scaling (3-10 replicas)
- **Performance Optimization**: Async processing, connection pooling, caching

### Technology Stack
- **Python 3.11+**: Core programming language
- **LlamaIndex Framework**: Document processing and indexing
- **OpenAI API**: Language model integration
- **FastAPI**: Modern REST API with security middleware
- **SQLAlchemy**: Database ORM with PostgreSQL support
- **Alembic**: Database migration management
- **Pytest**: Comprehensive testing framework
- **JWT**: Authentication infrastructure

## 📁 Project Structure

```
rag-agent-platform/
├── src/                    # Source code
│   ├── rag_agent/         # RAG platform core
│   │   ├── api_server.py  # FastAPI server with security
│   │   ├── security.py    # Security utilities (JWT, rate limiting)
│   │   ├── database.py    # Database models and persistence
│   │   ├── vector_store.py # Vector database integration
│   │   ├── web_ui.py      # Flask web interface
│   │   ├── agent_architecture/  # Agent implementations
│   │   └── traditional_rag/     # Traditional RAG examples
│   │
│   ├── shared/            # Shared utilities
│   └── examples/          # Example implementations
│
├── alembic/               # Database migrations
│   ├── versions/          # Migration scripts
│   └── env.py             # Alembic environment
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── data/                  # Data files (database, vector stores)
└── .env.example           # Environment configuration template
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+

### Setup
1. Clone the repository:
```bash
git clone https://github.com/vaibhav-dev-arch/rag-agent-platform.git
cd rag-agent-platform
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

6. Run database migration:
```bash
python -m alembic upgrade head
```

## 🚀 Quick Start

### Running the RAG Platform

1. **Start the API server**:
```bash
python -m src api
# or
python scripts/rag_platform.py api
```

2. **Start the web interface**:
```bash
python -m src web
# or
python scripts/rag_platform.py web
```

3. **Check API health**:
```bash
curl http://localhost:8000/health
```

### Using the RAG System

1. **API Usage**:
```python
import requests

# Query the RAG system
response = requests.post("http://localhost:8000/query", 
                        json={"query": "What is RAG?"})
print(response.json())
```

2. **Web Interface**:
- Open http://localhost:5000 in your browser
- Enter your query in the interface
- View results and generated responses

## 📚 Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference with security features
- [Agent Architecture](AGENT_ARCHITECTURE_README.md) - Agent system details
- [Phase 1 Complete](PHASE1_COMPLETE.md) - Phase 1 implementation summary
- [Production Readiness](PRODUCTION_READINESS_ASSESSMENT.md) - Production readiness assessment

## 🔒 Security Features

### Rate Limiting
- **IP-based rate limiting**: Configurable requests per minute
- **Endpoint-specific limits**: Different limits for queries, uploads, etc.
- **Redis support**: Optional Redis backend for distributed rate limiting
- **In-memory fallback**: Works without Redis for single-instance deployments

### Input Validation
- **Query validation**: Automatic sanitization and length limits
- **Document validation**: Size limits and content sanitization
- **SQL injection protection**: Parameterized queries
- **XSS protection**: Input sanitization

### CORS Configuration
- **Production-ready**: Configurable allowed origins
- **Development mode**: Allow all origins (configurable)
- **Security headers**: Ready for production deployment

### JWT Infrastructure
- **Token creation and verification**: Ready for optional authentication
- **Configurable expiration**: Token lifetime configuration
- **Production-ready**: Secure token handling

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ -v --cov=src --cov-report=html
```

Run specific test suites:
```bash
pytest tests/unit/ -v              # Unit tests
pytest tests/integration/ -v      # Integration tests
```

## 🔧 Configuration

### Environment Variables

#### Required
- `OPENAI_API_KEY`: Your OpenAI API key

#### Security (Optional but Recommended)
- `JWT_SECRET`: Secret for JWT tokens (use strong random string in production)
- `CORS_ORIGINS`: Allowed origins (`*` for dev, specific domain for prod)
- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: `true`)
- `RATE_LIMIT_REQUESTS`: Requests per window (default: `100`)
- `RATE_LIMIT_WINDOW`: Window in seconds (default: `60`)

#### Database (Optional - SQLite default)
- `DATABASE_URL`: Database connection string (e.g., `postgresql://user:pass@host/db`)
- `DATABASE_PATH`: SQLite database path (default: `data/rag_platform.db`)

#### Vector Store (Optional - in-memory default)
- `VECTOR_STORE_TYPE`: Type of vector store (`chroma`, `qdrant`, `pinecone`, or `in_memory`)
- See `.env.example` for vector store specific configuration

#### Other
- `OLLAMA_BASE_URL`: Ollama server URL (optional)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `MAX_QUERY_LENGTH`: Maximum query length (default: `2000`)
- `MAX_DOCUMENT_LENGTH`: Maximum document length (default: `100000`)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/vaibhav-dev-arch/rag-agent-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vaibhav-dev-arch/rag-agent-platform/discussions)
- **Documentation**: [Project Wiki](https://github.com/vaibhav-dev-arch/rag-agent-platform/wiki)

## 🗄️ Database & Persistence

### SQLite (Default)
- **Local development**: Zero configuration required
- **Automatic initialization**: Creates database on first run
- **File-based storage**: `data/rag_platform.db`

### PostgreSQL
- **Production-ready**: Full PostgreSQL support
- **Connection string**: `DATABASE_URL` environment variable
- **Schema migrations**: Alembic for database versioning

### Document Persistence
- **Automatic storage**: All documents saved to database
- **Metadata tracking**: Document source, timestamps, indexing status
- **Query history**: Complete audit trail of all queries

### Vector Database Support
- **Chroma**: Local, lightweight vector store (default)
- **Qdrant**: Production-ready vector database
- **Pinecone**: Managed cloud vector store
- **In-memory**: Fallback for testing

## 🔄 Database Migrations

### Initial Setup
```bash
# Create database tables
python -m alembic upgrade head
```

### Create New Migration
```bash
# After changing models
python -m alembic revision --autogenerate -m "Description"
python -m alembic upgrade head
```

## 🎯 Roadmap

### Completed ✅
- [x] Security hardening (rate limiting, validation, CORS)
- [x] Database persistence (SQLite & PostgreSQL)
- [x] Comprehensive testing infrastructure
- [x] Vector database support (multiple backends)
- [x] Database migrations (Alembic)

### In Progress
- [ ] Enhanced agent capabilities
- [ ] Additional LLM integrations
- [ ] Cloud deployment options (Docker, Kubernetes)

### Planned
- [ ] Performance optimizations
- [ ] Advanced monitoring and observability
- [ ] Load testing and optimization

## 🙏 Acknowledgments

- [LlamaIndex](https://github.com/jerryjliu/llama_index) for the RAG framework
- [OpenAI](https://openai.com/) for language models
- [Playwright](https://playwright.dev/) for browser automation
- [FFmpeg](https://ffmpeg.org/) for video processing
- [Microsoft Edge TTS](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/) for text-to-speech