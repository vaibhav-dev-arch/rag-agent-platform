#!/usr/bin/env python3
"""
System Architecture Video Generator for RAG Agent Platform
Creates a comprehensive architecture explanation video.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "videos"
TEMP_DIR = PROJECT_ROOT / "temp" / "architecture_video"
SLIDES_DIR = TEMP_DIR / "slides"

# Create directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
SLIDES_DIR.mkdir(parents=True, exist_ok=True)


class ArchitectureVideoGenerator:
    """Generate system architecture video for RAG Agent Platform."""
    
    def __init__(self):
        self.slides = []
        self.script = []
        self.output_video = OUTPUT_DIR / "rag_agent_platform_architecture.mp4"
    
    def generate_architecture_slides(self) -> List[Dict[str, Any]]:
        """Generate slides explaining the architecture."""
        slides = [
            {
                "title": "RAG Agent Platform",
                "subtitle": "System Architecture Overview",
                "content": """
                <div class="center-content">
                    <h1>RAG Agent Platform</h1>
                    <h2>System Architecture</h2>
                    <p>A comprehensive, production-ready RAG platform with<br/>
                    agent architecture, security, and database persistence</p>
                    <div class="tech-badges">
                        <span>FastAPI</span>
                        <span>LlamaIndex</span>
                        <span>OpenAI</span>
                        <span>SQLAlchemy</span>
                        <span>PostgreSQL</span>
                    </div>
                </div>
                """,
                "duration": 5.0
            },
            {
                "title": "Architecture Layers",
                "subtitle": "Three-Tier Architecture",
                "content": """
                <div class="architecture-layers">
                    <div class="layer">
                        <h3>🖥️ Presentation Layer</h3>
                        <ul>
                            <li>FastAPI REST API</li>
                            <li>Flask Web UI</li>
                            <li>API Documentation (Swagger)</li>
                        </ul>
                    </div>
                    <div class="layer">
                        <h3>🧠 Application Layer</h3>
                        <ul>
                            <li>ReActAgent (Reasoning & Acting)</li>
                            <li>RAG System (Retrieval-Augmented Generation)</li>
                            <li>Agent Tools & Memory</li>
                        </ul>
                    </div>
                    <div class="layer">
                        <h3>💾 Data Layer</h3>
                        <ul>
                            <li>Vector Store (Chroma/Qdrant/Pinecone)</li>
                            <li>PostgreSQL / SQLite</li>
                            <li>Document Storage</li>
                        </ul>
                    </div>
                </div>
                """,
                "duration": 8.0
            },
            {
                "title": "API Layer",
                "subtitle": "FastAPI REST API",
                "content": """
                <div class="component-detail">
                    <h3>FastAPI REST API</h3>
                    <div class="features">
                        <div class="feature-box">
                            <h4>🔒 Security</h4>
                            <ul>
                                <li>Rate Limiting (IP-based)</li>
                                <li>Input Validation</li>
                                <li>CORS Configuration</li>
                                <li>JWT Authentication</li>
                            </ul>
                        </div>
                        <div class="feature-box">
                            <h4>📊 Endpoints</h4>
                            <ul>
                                <li>/query - RAG queries</li>
                                <li>/agent/query - Agent queries</li>
                                <li>/documents - Document management</li>
                                <li>/health - Health checks</li>
                            </ul>
                        </div>
                    </div>
                </div>
                """,
                "duration": 7.0
            },
            {
                "title": "Agent Architecture",
                "subtitle": "ReActAgent with Tools",
                "content": """
                <div class="agent-architecture">
                    <div class="agent-flow">
                        <h3>ReActAgent Workflow</h3>
                        <div class="flow-diagram">
                            <div class="step">User Query</div>
                            <div class="arrow">→</div>
                            <div class="step">Agent Reasoning</div>
                            <div class="arrow">→</div>
                            <div class="step">Tool Selection</div>
                            <div class="arrow">→</div>
                            <div class="step">Tool Execution</div>
                            <div class="arrow">→</div>
                            <div class="step">Response Generation</div>
                        </div>
                    </div>
                    <div class="tools-list">
                        <h4>Available Tools:</h4>
                        <ul>
                            <li>📄 Document Search</li>
                            <li>🌐 Web Search</li>
                            <li>🔍 Web Scraping</li>
                            <li>🧮 Calculator</li>
                            <li>⏰ Time/Date</li>
                            <li>💭 Sentiment Analysis</li>
                            <li>📝 Text Summarization</li>
                        </ul>
                    </div>
                </div>
                """,
                "duration": 8.0
            },
            {
                "title": "RAG System",
                "subtitle": "Retrieval-Augmented Generation",
                "content": """
                <div class="rag-flow">
                    <h3>RAG Workflow</h3>
                    <div class="rag-steps">
                        <div class="rag-step">
                            <div class="step-number">1</div>
                            <h4>Document Indexing</h4>
                            <p>Documents are chunked and converted to embeddings</p>
                        </div>
                        <div class="rag-step">
                            <div class="step-number">2</div>
                            <h4>Vector Storage</h4>
                            <p>Embeddings stored in vector database (Chroma/Qdrant)</p>
                        </div>
                        <div class="rag-step">
                            <div class="step-number">3</div>
                            <h4>Query Processing</h4>
                            <p>Query converted to embedding for similarity search</p>
                        </div>
                        <div class="rag-step">
                            <div class="step-number">4</div>
                            <h4>Retrieval</h4>
                            <p>Top-K similar documents retrieved</p>
                        </div>
                        <div class="rag-step">
                            <div class="step-number">5</div>
                            <h4>Generation</h4>
                            <p>LLM generates response using retrieved context</p>
                        </div>
                    </div>
                </div>
                """,
                "duration": 10.0
            },
            {
                "title": "Data Layer",
                "subtitle": "Database & Storage",
                "content": """
                <div class="data-layer">
                    <div class="data-component">
                        <h3>📊 PostgreSQL / SQLite</h3>
                        <ul>
                            <li>Document Metadata Storage</li>
                            <li>Query History Tracking</li>
                            <li>User Management (future)</li>
                            <li>Schema Migrations (Alembic)</li>
                        </ul>
                    </div>
                    <div class="data-component">
                        <h3>🔍 Vector Database</h3>
                        <ul>
                            <li><strong>Chroma</strong> - Local, lightweight</li>
                            <li><strong>Qdrant</strong> - Production-ready</li>
                            <li><strong>Pinecone</strong> - Managed cloud</li>
                            <li>In-memory fallback for testing</li>
                        </ul>
                    </div>
                    <div class="data-component">
                        <h3>📁 Document Storage</h3>
                        <ul>
                            <li>Text documents</li>
                            <li>Web-scraped content</li>
                            <li>Metadata tracking</li>
                            <li>Indexing status</li>
                        </ul>
                    </div>
                </div>
                """,
                "duration": 8.0
            },
            {
                "title": "Security Layer",
                "subtitle": "Production-Ready Security",
                "content": """
                <div class="security-features">
                    <div class="security-box">
                        <h4>🛡️ Rate Limiting</h4>
                        <p>100 requests/minute per IP</p>
                        <p>Redis optional for distributed systems</p>
                        <p>In-memory fallback available</p>
                    </div>
                    <div class="security-box">
                        <h4>✅ Input Validation</h4>
                        <p>Query length limits (2000 chars)</p>
                        <p>Document size limits (100K chars)</p>
                        <p>Automatic sanitization</p>
                    </div>
                    <div class="security-box">
                        <h4>🔐 Authentication</h4>
                        <p>JWT token infrastructure</p>
                        <p>Optional authentication</p>
                        <p>Production-ready token handling</p>
                    </div>
                    <div class="security-box">
                        <h4>🌐 CORS</h4>
                        <p>Configurable allowed origins</p>
                        <p>Production mode restrictions</p>
                        <p>Security headers ready</p>
                    </div>
                </div>
                """,
                "duration": 7.0
            },
            {
                "title": "Technology Stack",
                "subtitle": "Core Technologies",
                "content": """
                <div class="tech-stack">
                    <div class="tech-category">
                        <h3>🔧 Framework & API</h3>
                        <ul>
                            <li>FastAPI - Modern REST API</li>
                            <li>Flask - Web UI</li>
                            <li>Uvicorn - ASGI server</li>
                        </ul>
                    </div>
                    <div class="tech-category">
                        <h3>🤖 AI & ML</h3>
                        <ul>
                            <li>LlamaIndex - RAG framework</li>
                            <li>OpenAI GPT-3.5-turbo - LLM</li>
                            <li>OpenAI Embeddings - text-embedding-3-small</li>
                        </ul>
                    </div>
                    <div class="tech-category">
                        <h3>💾 Database</h3>
                        <ul>
                            <li>SQLAlchemy - ORM</li>
                            <li>PostgreSQL - Production DB</li>
                            <li>SQLite - Development DB</li>
                            <li>Alembic - Migrations</li>
                        </ul>
                    </div>
                    <div class="tech-category">
                        <h3>🧪 Testing & DevOps</h3>
                        <ul>
                            <li>Pytest - Testing framework</li>
                            <li>GitHub Actions - CI/CD</li>
                            <li>Pre-commit hooks</li>
                        </ul>
                    </div>
                </div>
                """,
                "duration": 8.0
            },
            {
                "title": "Request Flow",
                "subtitle": "Complete Request Lifecycle",
                "content": """
                <div class="request-flow">
                    <div class="flow-step">
                        <div class="step-icon">1️⃣</div>
                        <h4>Client Request</h4>
                        <p>HTTP request to FastAPI endpoint</p>
                    </div>
                    <div class="arrow-down">↓</div>
                    <div class="flow-step">
                        <div class="step-icon">2️⃣</div>
                        <h4>Security Middleware</h4>
                        <p>Rate limiting, validation, CORS</p>
                    </div>
                    <div class="arrow-down">↓</div>
                    <div class="flow-step">
                        <div class="step-icon">3️⃣</div>
                        <h4>Agent Processing</h4>
                        <p>ReActAgent reasoning & tool selection</p>
                    </div>
                    <div class="arrow-down">↓</div>
                    <div class="flow-step">
                        <div class="step-icon">4️⃣</div>
                        <h4>Vector Retrieval</h4>
                        <p>Similarity search in vector database</p>
                    </div>
                    <div class="arrow-down">↓</div>
                    <div class="flow-step">
                        <div class="step-icon">5️⃣</div>
                        <h4>LLM Generation</h4>
                        <p>Context-aware response generation</p>
                    </div>
                    <div class="arrow-down">↓</div>
                    <div class="flow-step">
                        <div class="step-icon">6️⃣</div>
                        <h4>Response & History</h4>
                        <p>Return response, log to database</p>
                    </div>
                </div>
                """,
                "duration": 10.0
            },
            {
                "title": "Production Features",
                "subtitle": "Phase 1 Complete",
                "content": """
                <div class="production-features">
                    <div class="feature-grid">
                        <div class="feature-item">
                            <span class="checkmark">✅</span>
                            <h4>Testing</h4>
                            <p>30+ unit tests<br/>Integration tests<br/>Test fixtures</p>
                        </div>
                        <div class="feature-item">
                            <span class="checkmark">✅</span>
                            <h4>Security</h4>
                            <p>Rate limiting<br/>Input validation<br/>CORS & JWT</p>
                        </div>
                        <div class="feature-item">
                            <span class="checkmark">✅</span>
                            <h4>Database</h4>
                            <p>SQLite & PostgreSQL<br/>Document persistence<br/>Query history</p>
                        </div>
                        <div class="feature-item">
                            <span class="checkmark">✅</span>
                            <h4>Vector Store</h4>
                            <p>Chroma/Qdrant/Pinecone<br/>Multiple backends<br/>Persistent storage</p>
                        </div>
                        <div class="feature-item">
                            <span class="checkmark">✅</span>
                            <h4>Migrations</h4>
                            <p>Alembic configured<br/>Schema versioning<br/>Migration ready</p>
                        </div>
                        <div class="feature-item">
                            <span class="checkmark">✅</span>
                            <h4>Documentation</h4>
                            <p>API docs<br/>Architecture guides<br/>Production readiness</p>
                        </div>
                    </div>
                </div>
                """,
                "duration": 8.0
            },
            {
                "title": "Project Structure",
                "subtitle": "Code Organization",
                "content": """
                <div class="project-structure">
                    <pre><code>rag-agent-platform/
├── src/
│   ├── rag_agent/
│   │   ├── api_server.py      # FastAPI server
│   │   ├── security.py        # Security utilities
│   │   ├── database.py         # Database models
│   │   ├── vector_store.py    # Vector DB integration
│   │   └── agent_architecture/
│   ├── examples/              # Example implementations
│   └── shared/                # Shared utilities
├── tests/
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── alembic/                   # Database migrations
├── docs/                      # Documentation
└── scripts/                   # Utility scripts</code></pre>
                </div>
                """,
                "duration": 7.0
            },
            {
                "title": "Key Capabilities",
                "subtitle": "What This Platform Can Do",
                "content": """
                <div class="capabilities">
                    <div class="capability-list">
                        <div class="capability">
                            <h4>🔍 Document Q&A</h4>
                            <p>Ask questions about your indexed documents</p>
                        </div>
                        <div class="capability">
                            <h4>🤖 Intelligent Agents</h4>
                            <p>Agents that reason and use tools to solve problems</p>
                        </div>
                        <div class="capability">
                            <h4>🌐 Web Integration</h4>
                            <p>Search the web and scrape content</p>
                        </div>
                        <div class="capability">
                            <h4>📊 Query Analytics</h4>
                            <p>Track all queries and responses</p>
                        </div>
                        <div class="capability">
                            <h4>🔒 Production Security</h4>
                            <p>Rate limiting, validation, authentication</p>
                        </div>
                        <div class="capability">
                            <h4>💾 Data Persistence</h4>
                            <p>Documents and queries saved to database</p>
                        </div>
                    </div>
                </div>
                """,
                "duration": 8.0
            },
            {
                "title": "Use Cases",
                "subtitle": "Real-World Applications",
                "content": """
                <div class="use-cases">
                    <div class="use-case-grid">
                        <div class="use-case">
                            <h4>📚 Knowledge Base Q&A</h4>
                            <p>Enterprise document search and Q&A</p>
                        </div>
                        <div class="use-case">
                            <h4>💼 Customer Support</h4>
                            <p>AI-powered customer service agents</p>
                        </div>
                        <div class="use-case">
                            <h4>🔬 Research Assistant</h4>
                            <p>Research document analysis and synthesis</p>
                        </div>
                        <div class="use-case">
                            <h4>⚖️ Legal Document Analysis</h4>
                            <p>Specialized legal agent for document review</p>
                        </div>
                        <div class="use-case">
                            <h4>🏥 Healthcare Information</h4>
                            <p>Medical document Q&A and analysis</p>
                        </div>
                        <div class="use-case">
                            <h4>📊 Business Intelligence</h4>
                            <p>Analyze business documents and reports</p>
                        </div>
                    </div>
                </div>
                """,
                "duration": 8.0
            },
            {
                "title": "Production Readiness",
                "subtitle": "65/100 - Getting Production Ready",
                "content": """
                <div class="readiness">
                    <div class="readiness-scores">
                        <div class="score-item">
                            <h4>Testing</h4>
                            <div class="score-bar">
                                <div class="score-fill" style="width: 80%">8/10</div>
                            </div>
                        </div>
                        <div class="score-item">
                            <h4>Security</h4>
                            <div class="score-bar">
                                <div class="score-fill" style="width: 80%">8/10</div>
                            </div>
                        </div>
                        <div class="score-item">
                            <h4>Database</h4>
                            <div class="score-bar">
                                <div class="score-fill" style="width: 80%">8/10</div>
                            </div>
                        </div>
                        <div class="score-item">
                            <h4>Architecture</h4>
                            <div class="score-bar">
                                <div class="score-fill" style="width: 70%">7/10</div>
                            </div>
                        </div>
                        <div class="score-item">
                            <h4>Documentation</h4>
                            <div class="score-bar">
                                <div class="score-fill" style="width: 80%">8/10</div>
                            </div>
                        </div>
                        <div class="score-total">
                            <h3>Overall: 65/100</h3>
                            <p>Phase 1 Complete ✅</p>
                        </div>
                    </div>
                </div>
                """,
                "duration": 7.0
            },
            {
                "title": "Thank You!",
                "subtitle": "RAG Agent Platform",
                "content": """
                <div class="center-content">
                    <h1>RAG Agent Platform</h1>
                    <h2>System Architecture</h2>
                    <div class="contact-info">
                        <p>📍 GitHub: github.com/vaibhav-dev-arch/rag-agent-platform</p>
                        <p>📚 Documentation: See docs/ folder</p>
                        <p>🚀 Ready for Production Use</p>
                    </div>
                    <div class="tech-badges">
                        <span>Production-Ready</span>
                        <span>Secure</span>
                        <span>Scalable</span>
                        <span>Well-Tested</span>
                    </div>
                </div>
                """,
                "duration": 5.0
            }
        ]
        
        return slides
    
    def generate_narration_script(self, slides: List[Dict[str, Any]]) -> str:
        """Generate narration script for the video."""
        script_parts = [
            "Welcome to the RAG Agent Platform System Architecture overview.",
            "This video will explain the complete architecture of our production-ready RAG platform.",
            "",
            "The platform follows a three-tier architecture with Presentation, Application, and Data layers.",
            "The Presentation Layer includes FastAPI REST API and Flask Web UI.",
            "The Application Layer contains our ReActAgent with RAG system and agent tools.",
            "The Data Layer includes vector stores, PostgreSQL or SQLite databases, and document storage.",
            "",
            "Our FastAPI REST API provides a comprehensive set of endpoints with production-ready security.",
            "Features include rate limiting, input validation, CORS configuration, and JWT authentication infrastructure.",
            "Key endpoints include query for RAG queries, agent query for agent-based interactions, and document management.",
            "",
            "The Agent Architecture uses ReActAgent, which stands for Reasoning and Acting.",
            "The agent follows a workflow: receiving user queries, reasoning about the task, selecting appropriate tools, executing them, and generating responses.",
            "Available tools include document search, web search, web scraping, calculator, time and date, sentiment analysis, and text summarization.",
            "",
            "The RAG System implements Retrieval-Augmented Generation with a five-step workflow.",
            "First, documents are chunked and converted to embeddings using text-embedding-3-small.",
            "Second, embeddings are stored in a vector database such as Chroma, Qdrant, or Pinecone.",
            "Third, user queries are converted to embeddings for similarity search.",
            "Fourth, the top K most similar documents are retrieved.",
            "Fifth, the LLM generates responses using the retrieved context.",
            "",
            "Our Data Layer consists of multiple storage solutions.",
            "PostgreSQL or SQLite stores document metadata, query history, and will support user management in the future.",
            "Schema migrations are handled by Alembic.",
            "Vector databases store document embeddings, with support for Chroma, Qdrant, and Pinecone.",
            "Document storage tracks text content, metadata, and indexing status.",
            "",
            "Security is a top priority with multiple layers of protection.",
            "Rate limiting prevents abuse with 100 requests per minute per IP, with Redis support for distributed systems.",
            "Input validation ensures query and document length limits are enforced with automatic sanitization.",
            "JWT authentication infrastructure is ready for optional authentication.",
            "CORS configuration allows for production-ready origin restrictions.",
            "",
            "Our technology stack is modern and production-ready.",
            "FastAPI provides a modern REST API, while Flask handles the web interface.",
            "LlamaIndex powers our RAG framework with OpenAI GPT-3.5-turbo for language generation.",
            "SQLAlchemy with PostgreSQL or SQLite provides robust data persistence.",
            "Pytest ensures comprehensive testing coverage.",
            "",
            "Let's trace a complete request lifecycle.",
            "A client sends an HTTP request to a FastAPI endpoint.",
            "Security middleware applies rate limiting, input validation, and CORS checks.",
            "The agent processes the request using reasoning and tool selection.",
            "Vector retrieval performs similarity search in the vector database.",
            "The LLM generates context-aware responses.",
            "Finally, the response is returned and logged to the database.",
            "",
            "Phase 1 of our production readiness journey is complete.",
            "We have comprehensive testing with 30 plus unit tests and integration tests.",
            "Security features include rate limiting, validation, CORS, and JWT infrastructure.",
            "Database persistence supports both SQLite and PostgreSQL with Alembic migrations.",
            "Vector store support includes Chroma, Qdrant, and Pinecone.",
            "Extensive documentation covers API, architecture, and production readiness.",
            "",
            "The project structure is well-organized with clear separation of concerns.",
            "Source code is in the src directory, with rag_agent containing core functionality.",
            "Tests are organized into unit and integration test suites.",
            "Alembic handles database migrations, and documentation is comprehensive.",
            "",
            "Key capabilities include document Q and A, intelligent agents that reason and use tools, web integration for search and scraping, query analytics tracking, production security features, and data persistence.",
            "",
            "Use cases span multiple industries including knowledge base Q and A for enterprises, customer support agents, research assistants, legal document analysis, healthcare information systems, and business intelligence.",
            "",
            "Our production readiness score is 65 out of 100, with Phase 1 complete.",
            "Testing scores 8 out of 10, Security 8 out of 10, Database 8 out of 10, Architecture 7 out of 10, and Documentation 8 out of 10.",
            "",
            "Thank you for watching the RAG Agent Platform System Architecture overview.",
            "The platform is production-ready with security, database persistence, comprehensive testing, and extensive documentation.",
            "Visit our GitHub repository for more information and documentation."
        ]
        
        return " ".join(script_parts)
    
    def create_slide_html(self, slide: Dict[str, Any], slide_num: int) -> str:
        """Create HTML for a slide."""
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{slide['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            width: 1920px;
            height: 1080px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        
        .slide-container {{
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            width: 90%;
            height: 85%;
            border-radius: 20px;
            padding: 60px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
        }}
        
        .slide-title {{
            font-size: 48px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .slide-subtitle {{
            font-size: 32px;
            color: #764ba2;
            margin-bottom: 40px;
            text-align: center;
            font-weight: 300;
        }}
        
        .slide-content {{
            flex: 1;
            font-size: 24px;
            line-height: 1.6;
            overflow-y: auto;
        }}
        
        .center-content {{
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
        }}
        
        .center-content h1 {{
            font-size: 72px;
            color: #667eea;
            margin-bottom: 30px;
        }}
        
        .center-content h2 {{
            font-size: 48px;
            color: #764ba2;
            margin-bottom: 40px;
        }}
        
        .tech-badges {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 40px;
        }}
        
        .tech-badges span {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 30px;
            font-size: 20px;
            font-weight: 600;
        }}
        
        .architecture-layers {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            height: 100%;
        }}
        
        .layer {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 15px;
            border: 3px solid #667eea;
        }}
        
        .layer h3 {{
            font-size: 28px;
            margin-bottom: 20px;
            color: #667eea;
        }}
        
        .layer ul {{
            list-style: none;
            font-size: 20px;
        }}
        
        .layer li {{
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
        }}
        
        .component-detail {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
            height: 100%;
        }}
        
        .feature-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 15px;
            border: 3px solid #764ba2;
        }}
        
        .feature-box h4 {{
            font-size: 28px;
            margin-bottom: 20px;
            color: #764ba2;
        }}
        
        .feature-box ul {{
            list-style: none;
            font-size: 20px;
        }}
        
        .feature-box li {{
            padding: 8px 0;
        }}
        
        .agent-flow {{
            margin-bottom: 30px;
        }}
        
        .flow-diagram {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #f5f7fa;
            padding: 30px;
            border-radius: 15px;
            margin-top: 20px;
        }}
        
        .flow-diagram .step {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            text-align: center;
            min-width: 150px;
        }}
        
        .flow-diagram .arrow {{
            font-size: 36px;
            color: #667eea;
            font-weight: bold;
        }}
        
        .tools-list {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 15px;
        }}
        
        .tools-list h4 {{
            font-size: 28px;
            margin-bottom: 20px;
            color: #667eea;
        }}
        
        .tools-list ul {{
            list-style: none;
            font-size: 20px;
        }}
        
        .tools-list li {{
            padding: 10px 0;
        }}
        
        .rag-steps {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            margin-top: 30px;
        }}
        
        .rag-step {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border: 3px solid #667eea;
        }}
        
        .step-number {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            margin: 0 auto 15px;
        }}
        
        .rag-step h4 {{
            font-size: 22px;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .rag-step p {{
            font-size: 16px;
            color: #666;
        }}
        
        .data-layer {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            height: 100%;
        }}
        
        .data-component {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 15px;
            border: 3px solid #667eea;
        }}
        
        .data-component h3 {{
            font-size: 28px;
            margin-bottom: 20px;
            color: #667eea;
        }}
        
        .data-component ul {{
            list-style: none;
            font-size: 18px;
        }}
        
        .data-component li {{
            padding: 8px 0;
        }}
        
        .security-features {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
            height: 100%;
        }}
        
        .security-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 15px;
            border: 3px solid #764ba2;
        }}
        
        .security-box h4 {{
            font-size: 28px;
            margin-bottom: 15px;
            color: #764ba2;
        }}
        
        .security-box p {{
            font-size: 18px;
            margin: 8px 0;
            color: #666;
        }}
        
        .tech-stack {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
            height: 100%;
        }}
        
        .tech-category {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 15px;
            border: 3px solid #667eea;
        }}
        
        .tech-category h3 {{
            font-size: 28px;
            margin-bottom: 20px;
            color: #667eea;
        }}
        
        .tech-category ul {{
            list-style: none;
            font-size: 18px;
        }}
        
        .tech-category li {{
            padding: 8px 0;
        }}
        
        .request-flow {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            height: 100%;
            justify-content: center;
        }}
        
        .flow-step {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px 40px;
            border-radius: 15px;
            border: 3px solid #667eea;
            text-align: center;
            min-width: 400px;
        }}
        
        .step-icon {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        
        .flow-step h4 {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .flow-step p {{
            font-size: 18px;
            color: #666;
        }}
        
        .arrow-down {{
            font-size: 36px;
            color: #667eea;
            font-weight: bold;
        }}
        
        .production-features {{
            height: 100%;
        }}
        
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
            height: 100%;
        }}
        
        .feature-item {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 15px;
            border: 3px solid #667eea;
            text-align: center;
        }}
        
        .checkmark {{
            font-size: 36px;
            display: block;
            margin-bottom: 10px;
        }}
        
        .feature-item h4 {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 15px;
        }}
        
        .feature-item p {{
            font-size: 16px;
            color: #666;
        }}
        
        .project-structure {{
            background: #1e1e1e;
            padding: 30px;
            border-radius: 15px;
            height: 100%;
            overflow: auto;
        }}
        
        .project-structure pre {{
            color: #d4d4d4;
            font-size: 20px;
            line-height: 1.6;
        }}
        
        .capabilities {{
            height: 100%;
        }}
        
        .capability-list {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
            height: 100%;
        }}
        
        .capability {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 15px;
            border: 3px solid #667eea;
        }}
        
        .capability h4 {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .capability p {{
            font-size: 18px;
            color: #666;
        }}
        
        .use-cases {{
            height: 100%;
        }}
        
        .use-case-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
            height: 100%;
        }}
        
        .use-case {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 15px;
            border: 3px solid #764ba2;
        }}
        
        .use-case h4 {{
            font-size: 24px;
            color: #764ba2;
            margin-bottom: 10px;
        }}
        
        .use-case p {{
            font-size: 18px;
            color: #666;
        }}
        
        .readiness {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .readiness-scores {{
            width: 80%;
        }}
        
        .score-item {{
            margin-bottom: 25px;
        }}
        
        .score-item h4 {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .score-bar {{
            background: #e0e0e0;
            height: 40px;
            border-radius: 20px;
            overflow: hidden;
        }}
        
        .score-fill {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }}
        
        .score-total {{
            text-align: center;
            margin-top: 40px;
        }}
        
        .score-total h3 {{
            font-size: 36px;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .score-total p {{
            font-size: 24px;
            color: #764ba2;
        }}
        
        .contact-info {{
            margin-top: 40px;
            font-size: 24px;
            color: #666;
        }}
        
        .contact-info p {{
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="slide-title">{slide['title']}</div>
        <div class="slide-subtitle">{slide['subtitle']}</div>
        <div class="slide-content">
            {slide['content']}
        </div>
    </div>
</body>
</html>
        """
        return html_template
    
    async def generate_slide_images(self):
        """Generate images from HTML slides using Playwright."""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(viewport={"width": 1920, "height": 1080})
                
                for i, slide in enumerate(self.slides):
                    html_content = self.create_slide_html(slide, i)
                    html_file = SLIDES_DIR / f"slide_{i:03d}.html"
                    html_file.write_text(html_content)
                    
                    await page.goto(f"file://{html_file.absolute()}")
                    await page.wait_for_timeout(1000)  # Wait for rendering
                    
                    image_path = SLIDES_DIR / f"slide_{i:03d}.png"
                    await page.screenshot(path=str(image_path), full_page=False)
                    print(f"✅ Generated slide {i+1}/{len(self.slides)}")
                
                await browser.close()
        except ImportError:
            print("⚠️  Playwright not installed. Install with: pip install playwright && playwright install")
            print("    Falling back to HTML files only.")
    
    async def generate_narration_audio(self, script: str) -> Path:
        """Generate audio narration using edge-tts."""
        audio_path = TEMP_DIR / "narration.wav"
        
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(script, "en-US-AriaNeural")
            await communicate.save(str(audio_path))
            print(f"✅ Generated narration audio: {audio_path}")
            return audio_path
        except ImportError:
            print("⚠️  edge-tts not installed. Install with: pip install edge-tts")
            print("    Creating silent video (narration will be missing).")
            # Create empty audio file
            audio_path.touch()
            return audio_path
        except Exception as e:
            print(f"⚠️  Error generating audio: {e}")
            audio_path.touch()
            return audio_path
    
    def create_video(self, narration_audio: Path) -> Path:
        """Create final video from slides and narration."""
        # Create video segments
        segments = []
        
        for i, slide in enumerate(self.slides):
            image_path = SLIDES_DIR / f"slide_{i:03d}.png"
            if not image_path.exists():
                print(f"⚠️  Slide {i} image not found, skipping...")
                continue
            
            duration = slide['duration']
            segment_path = TEMP_DIR / f"segment_{i:03d}.mp4"
            
            # Create video segment from image
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(image_path),
                "-t", str(duration),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                str(segment_path)
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                segments.append(segment_path)
                print(f"✅ Created segment {i+1}/{len(self.slides)}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Error creating segment {i}: {e.stderr.decode()}")
        
        if not segments:
            raise ValueError("No video segments created")
        
        # Create concat file
        concat_file = TEMP_DIR / "concat.txt"
        with open(concat_file, "w") as f:
            for segment in segments:
                f.write(f"file '{segment.absolute()}'\n")
        
        # Concatenate segments
        combined_video = TEMP_DIR / "combined.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(combined_video)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ Combined video segments")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Error combining segments: {e.stderr.decode()}")
            raise
        
        # Add narration
        if narration_audio.exists() and narration_audio.stat().st_size > 0:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(combined_video),
                "-i", str(narration_audio),
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(self.output_video)
            ]
        else:
            # No audio, just copy video
            combined_video.rename(self.output_video)
            return self.output_video
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Created final video: {self.output_video}")
            return self.output_video
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Error adding audio: {e.stderr.decode()}")
            # Fallback: just copy video without audio
            combined_video.rename(self.output_video)
            return self.output_video
    
    async def generate(self):
        """Generate the complete architecture video."""
        print("🎬 Starting Architecture Video Generation...")
        print("=" * 50)
        
        # Generate slides
        print("\n📊 Generating slides...")
        self.slides = self.generate_architecture_slides()
        print(f"✅ Created {len(self.slides)} slides")
        
        # Generate narration script
        print("\n📝 Generating narration script...")
        script = self.generate_narration_script(self.slides)
        print(f"✅ Script generated ({len(script)} characters)")
        
        # Generate slide images
        print("\n🖼️  Generating slide images...")
        await self.generate_slide_images()
        
        # Generate narration audio
        print("\n🔊 Generating narration audio...")
        narration_audio = await self.generate_narration_audio(script)
        
        # Create final video
        print("\n🎥 Creating final video...")
        video_path = self.create_video(narration_audio)
        
        print("\n" + "=" * 50)
        print(f"✅ Architecture video generated successfully!")
        print(f"📹 Output: {video_path}")
        print(f"📊 Total slides: {len(self.slides)}")
        total_duration = sum(slide.get('duration', 5.0) for slide in self.slides)
        print(f"⏱️  Approximate duration: {total_duration:.1f} seconds")
        print("=" * 50)
        
        return video_path


async def main():
    """Main entry point."""
    generator = ArchitectureVideoGenerator()
    await generator.generate()


if __name__ == "__main__":
    asyncio.run(main())

