import os
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from llama_index import VectorStoreIndex, Settings, Document
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.node_parser import SentenceSplitter
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.core.memory import ChatMemoryBuffer
import uvicorn
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

# Import security utilities
from .security import (
    validate_query as validate_query_input,
    validate_document_text,
    get_optional_user,
    check_rate_limit,
    get_client_ip,
    rate_limit_middleware
)

# Import database utilities
from .database import get_database, init_database, DatabaseManager

# Import monitoring utilities
from .monitoring import (
    init_monitoring,
    track_request,
    track_rag_query,
    track_agent_query,
    track_db_query,
    update_documents_count,
    update_vector_index_size,
    structured_log,
    performance_monitor,
    get_metrics
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Agent Platform API",
    description="A comprehensive RAG platform with agent architecture using LlamaIndex and OpenAI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware - Configure for production
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
if cors_origins == ["*"]:
    # Development mode - allow all origins
    allow_origins = ["*"]
else:
    # Production mode - specific origins
    allow_origins = [origin.strip() for origin in cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
llm = None
embed_model = None
index = None
documents = []
agent = None
agent_memory = None
db: DatabaseManager = None

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask")
    include_sources: bool = Field(True, description="Whether to include source information")

class AgentQueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask the agent")
    use_memory: bool = Field(True, description="Whether to use conversation memory")
    tools: Optional[List[str]] = Field(None, description="Specific tools to use (optional)")

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    query: str
    processing_time: float

class AgentResponse(BaseModel):
    answer: str
    tools_used: List[str] = []
    query: str
    processing_time: float
    memory_used: bool = False

class DocumentRequest(BaseModel):
    text: str = Field(..., description="Document text content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class WebScrapeRequest(BaseModel):
    urls: List[str] = Field(..., description="List of URLs to scrape")
    chunk_size: int = Field(1024, description="Text chunk size")
    chunk_overlap: int = Field(20, description="Chunk overlap")

class IndexStatus(BaseModel):
    has_index: bool
    document_count: int
    node_count: int
    is_configured: bool

class HealthResponse(BaseModel):
    status: str
    openai_configured: bool
    index_ready: bool
    agent_ready: bool
    message: str

class AgentToolsResponse(BaseModel):
    available_tools: List[str]
    tool_descriptions: Dict[str, str]

def setup_llamaindex():
    """Setup LlamaIndex with OpenAI configuration"""
    global llm, embed_model
    
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    llm = OpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
    
    return llm, embed_model

# Agent Tools
def document_search_tool(query: str) -> str:
    """Search through indexed documents"""
    try:
        global index
        if index is None:
            return "No documents indexed yet. Please add documents first."
        
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return str(response)
    except Exception as e:
        return f"Error searching documents: {str(e)}"

def web_search_tool(query: str) -> str:
    """Search the web for current information"""
    try:
        # Mock implementation - replace with real search API
        search_results = {
            "artificial intelligence": "AI is revolutionizing industries with applications in healthcare, finance, transportation, and more.",
            "machine learning": "ML enables computers to learn and improve from experience without being explicitly programmed.",
            "llamaindex": "LlamaIndex is a data framework for LLM applications that helps structure and access data for language models.",
            "rag": "Retrieval-Augmented Generation combines information retrieval with text generation for more accurate responses."
        }
        
        return search_results.get(query.lower(), f"Web search results for '{query}': Information not found in mock database.")
    except Exception as e:
        return f"Error searching web: {str(e)}"

def web_scrape_tool(url: str) -> str:
    """Scrape content from a web page"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:2000] + "..." if len(text) > 2000 else text
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

def calculate_tool(expression: str) -> str:
    """Perform mathematical calculations"""
    try:
        # Simple calculation - in production, use a proper math parser
        allowed_chars = set('0123456789+-*/()., ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression)
        return f"Calculation result: {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

def get_time_tool() -> str:
    """Get current date and time"""
    now = datetime.now()
    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

def analyze_sentiment_tool(text: str) -> str:
    """Analyze sentiment of text"""
    try:
        # Simple sentiment analysis - in production, use a proper NLP library
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "Positive"
        elif negative_count > positive_count:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        return f"Sentiment analysis: {sentiment} (Positive: {positive_count}, Negative: {negative_count})"
    except Exception as e:
        return f"Error analyzing sentiment: {str(e)}"

def summarize_text_tool(text: str) -> str:
    """Summarize long text"""
    try:
        if len(text) < 100:
            return "Text is too short to summarize meaningfully."
        
        # Simple summarization - in production, use a proper summarization model
        sentences = text.split('.')
        if len(sentences) <= 3:
            return text
        
        # Take first and last sentences as summary
        summary = sentences[0] + ". " + sentences[-1] + "."
        return f"Summary: {summary}"
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def create_agent():
    """Create the RAG agent with tools"""
    global agent, agent_memory
    
    # Create memory
    agent_memory = ChatMemoryBuffer.from_defaults(token_limit=2000)
    
    # Define tools
    tools = [
        FunctionTool.from_defaults(fn=document_search_tool, name="document_search"),
        FunctionTool.from_defaults(fn=web_search_tool, name="web_search"),
        FunctionTool.from_defaults(fn=web_scrape_tool, name="web_scrape"),
        FunctionTool.from_defaults(fn=calculate_tool, name="calculate"),
        FunctionTool.from_defaults(fn=get_time_tool, name="get_time"),
        FunctionTool.from_defaults(fn=analyze_sentiment_tool, name="analyze_sentiment"),
        FunctionTool.from_defaults(fn=summarize_text_tool, name="summarize_text"),
    ]
    
    # Create agent
    agent = ReActAgent.from_tools(
        tools=tools,
        llm=llm,
        memory=agent_memory,
        verbose=True,
        system_prompt="""You are an advanced AI assistant with access to multiple tools and capabilities.

        Your capabilities include:
        - Searching through indexed documents
        - Web search for current information
        - Web scraping from URLs
        - Mathematical calculations
        - Time and date information
        - Sentiment analysis
        - Text summarization

        Always use the most appropriate tool(s) to answer user questions.
        If you need multiple pieces of information, use multiple tools.
        Be thorough, accurate, and provide comprehensive answers.
        Remember previous conversation context and build upon it.
        
        When uncertain, ask clarifying questions rather than making assumptions."""
    )
    
    return agent

def create_index_from_documents(docs: List[Document]):
    """Create a vector index from documents"""
    global index
    
    if not docs:
        index = None
        return None
    
    try:
        index = VectorStoreIndex.from_documents(docs)
        return index
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating index: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database, LlamaIndex, Agent, and monitoring on startup"""
    global db
    try:
        # Initialize monitoring first
        sentry_dsn = os.getenv("SENTRY_DSN")
        environment = os.getenv("ENVIRONMENT", "production")
        init_monitoring(sentry_dsn=sentry_dsn, environment=environment)
        
        # Initialize database first
        db = init_database()
        structured_log("INFO", "Database initialized successfully")
        print("✅ Database initialized successfully")
        
        # Initialize LlamaIndex
        setup_llamaindex()
        
        # Create agent
        create_agent()
        structured_log("INFO", "LlamaIndex and Agent initialized successfully")
        print("✅ LlamaIndex and Agent initialized successfully")
        
        # Load existing documents from database
        if db:
            try:
                from llama_index import Document
                db_docs = db.get_all_documents(limit=1000)
                if db_docs:
                    documents.clear()
                    for db_doc in db_docs:
                        if db_doc.indexed:
                            doc = Document(text=db_doc.text, metadata=db_doc.doc_metadata)
                            documents.append(doc)
                    
                    if documents:
                        create_index_from_documents(documents)
                        update_documents_count(len(documents))
                        structured_log("INFO", f"Loaded {len(documents)} documents from database", document_count=len(documents))
                        print(f"✅ Loaded {len(documents)} documents from database")
            except Exception as e:
                error_msg = str(e)
                structured_log("WARNING", "Failed to load documents from database", error=error_msg)
                print(f"⚠️  Warning: Failed to load documents from database: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        structured_log("ERROR", "Error during startup", error=error_msg, traceback=str(e.__class__.__name__))
        print(f"❌ Error during startup: {error_msg}")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health and configuration status of the API"""
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    index_ready = index is not None
    agent_ready = agent is not None
    db_ready = db is not None
    
    # Check database connectivity
    db_healthy = False
    if db:
        try:
            # Try to query database
            db.get_all_documents(limit=1)
            db_healthy = True
        except Exception:
            db_healthy = False
    
    all_ready = all([openai_configured, index_ready, agent_ready, db_healthy])
    status = "healthy" if all_ready else "degraded"
    message = "API is ready" if status == "healthy" else "Some components are not ready"
    
    return HealthResponse(
        status=status,
        openai_configured=openai_configured,
        index_ready=index_ready,
        agent_ready=agent_ready,
        message=message
    )

# Detailed health check endpoint
@app.get("/health/detailed")
async def detailed_health_check():
    """Comprehensive health check with all dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "checks": {
            "openai": {
                "configured": bool(os.getenv("OPENAI_API_KEY")),
                "status": "ok" if os.getenv("OPENAI_API_KEY") else "missing"
            },
            "database": {
                "configured": db is not None,
                "connected": False,
                "status": "unknown"
            },
            "vector_index": {
                "exists": index is not None,
                "document_count": len(documents) if documents else 0,
                "status": "ok" if index is not None else "not_initialized"
            },
            "agent": {
                "initialized": agent is not None,
                "status": "ok" if agent is not None else "not_initialized"
            }
        },
        "performance": performance_monitor.get_stats()
    }
    
    # Check database connectivity
    if db:
        try:
            db.get_all_documents(limit=1)
            health_status["checks"]["database"]["connected"] = True
            health_status["checks"]["database"]["status"] = "ok"
        except Exception as e:
            health_status["checks"]["database"]["connected"] = False
            health_status["checks"]["database"]["status"] = "error"
            health_status["checks"]["database"]["error"] = str(e)
            health_status["status"] = "degraded"
    
    # Determine overall status
    if not all([
        health_status["checks"]["openai"]["configured"],
        health_status["checks"]["database"]["connected"],
        health_status["checks"]["vector_index"]["exists"]
    ]):
        health_status["status"] = "degraded"
    
    return health_status

# Metrics endpoint for Prometheus
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import Response
    metrics_data = get_metrics()
    return Response(content=metrics_data, media_type="text/plain")

# Get index status
@app.get("/status", response_model=IndexStatus)
async def get_index_status():
    """Get current status of the vector index and documents"""
    if index is None:
        return IndexStatus(
            has_index=False,
            document_count=0,
            node_count=0,
            is_configured=bool(os.getenv("OPENAI_API_KEY"))
        )
    
    try:
        # Get document count
        doc_count = len(documents)
        
        # Get node count (approximate)
        node_count = doc_count * 3  # Rough estimate
        
        return IndexStatus(
            has_index=True,
            document_count=doc_count,
            node_count=node_count,
            is_configured=bool(os.getenv("OPENAI_API_KEY"))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

# Traditional RAG query endpoint
@app.post("/query", response_model=QueryResponse)
async def query_index(request: QueryRequest, req: Request = None):
    """Query the vector index with a question"""
    start_time = time.time()
    success = False
    
    try:
        # Rate limiting
        if req:
            client_id = get_client_ip(req) or "anonymous"
            check_rate_limit(client_id, "query")
        
        # Input validation
        query = validate_query_input(request.query)
        
        if index is None:
            raise HTTPException(status_code=400, detail="No documents indexed yet. Please add documents first.")
        
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        
        processing_time = time.time() - start_time
        success = True
        
        # Track metrics
        track_rag_query(status="success", duration=processing_time)
        performance_monitor.record_request(processing_time, success=True)
        
        if req:
            track_request(method=req.method, endpoint=req.url.path, status=200, duration=processing_time)
        
        # Extract sources if requested
        sources = []
        if request.include_sources and hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                sources.append({
                    "text": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                    "score": node.score,
                    "metadata": node.metadata
                })
        
        # Save query history to database
        if db:
            try:
                db_operation_start = time.time()
                db.add_query_history(
                    query=query,
                    response=str(response)[:500],  # Truncate for storage
                    processing_time=int(processing_time * 1000),  # Convert to milliseconds
                    sources_count=len(sources)
                )
                db_duration = time.time() - db_operation_start
                track_db_query("add_query_history", "success", db_duration)
            except Exception as e:
                db_duration = time.time() - db_operation_start if 'db_operation_start' in locals() else 0
                track_db_query("add_query_history", "error", db_duration)
                structured_log("WARNING", "Failed to save query history", error=str(e))
        
        structured_log("INFO", "RAG query processed", query_length=len(query), processing_time=processing_time, sources_count=len(sources))
        
        return QueryResponse(
            answer=str(response),
            sources=sources,
            query=query,  # Use validated query
            processing_time=processing_time
        )
    except HTTPException as e:
        processing_time = time.time() - start_time
        track_rag_query(status="error", duration=processing_time)
        performance_monitor.record_request(processing_time, success=False)
        if req:
            track_request(method=req.method, endpoint=req.url.path, status=e.status_code, duration=processing_time)
        structured_log("WARNING", "RAG query failed", status_code=e.status_code, detail=e.detail)
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        track_rag_query(status="error", duration=processing_time)
        performance_monitor.record_request(processing_time, success=False)
        if req:
            track_request(method=req.method, endpoint=req.url.path, status=500, duration=processing_time)
        error_msg = str(e)
        structured_log("ERROR", "Error querying index", error=error_msg, traceback=str(e.__class__.__name__))
        raise HTTPException(status_code=500, detail=f"Error querying index: {error_msg}")

# NEW: Agent query endpoint
@app.post("/agent/query", response_model=AgentResponse)
async def agent_query(request: AgentQueryRequest):
    """Query the agent with advanced capabilities"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    start_time = time.time()
    
    try:
        # Use memory if requested
        if not request.use_memory:
            agent.memory.reset()
        
        # Get agent response
        response = agent.chat(request.query)
        
        processing_time = time.time() - start_time
        
        # Extract tools used (this would need to be implemented in the agent)
        tools_used = ["document_search", "web_search"]  # Mock implementation
        
        return AgentResponse(
            answer=str(response),
            tools_used=tools_used,
            query=request.query,
            processing_time=processing_time,
            memory_used=request.use_memory
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in agent query: {str(e)}")

# NEW: Get available agent tools
@app.get("/agent/tools", response_model=AgentToolsResponse)
async def get_agent_tools():
    """Get list of available agent tools"""
    tools = [
        "document_search",
        "web_search", 
        "web_scrape",
        "calculate",
        "get_time",
        "analyze_sentiment",
        "summarize_text"
    ]
    
    descriptions = {
        "document_search": "Search through indexed documents",
        "web_search": "Search the web for current information",
        "web_scrape": "Scrape content from web pages",
        "calculate": "Perform mathematical calculations",
        "get_time": "Get current date and time",
        "analyze_sentiment": "Analyze sentiment of text",
        "summarize_text": "Summarize long text"
    }
    
    return AgentToolsResponse(
        available_tools=tools,
        tool_descriptions=descriptions
    )

# NEW: Clear agent memory
@app.post("/agent/clear-memory")
async def clear_agent_memory():
    """Clear the agent's conversation memory"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        agent.memory.reset()
        return {"message": "Agent memory cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

# Add document endpoint
@app.post("/documents")
async def add_document(request: DocumentRequest, req: Request = None):
    """Add a document to the index"""
    global db
    # Rate limiting
    if req:
        client_id = get_client_ip(req) or "anonymous"
        check_rate_limit(client_id, "document_upload")
    
    # Input validation
    try:
        validated_text = validate_document_text(request.text)
        doc = Document(
            text=validated_text,
            metadata=request.metadata or {}
        )
        
        # Add to database first
        doc_id = None
        if db:
            doc_id = db.add_document(
                text=validated_text,
                metadata=request.metadata or {},
                source=(request.metadata.get("source", "api") if request.metadata else "api")
            )
        
        documents.append(doc)
        create_index_from_documents(documents)
        
        return {
            "message": "Document added successfully",
            "document_count": len(documents),
            "document_id": doc_id if doc_id else len(documents) - 1
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

# Web scraping endpoint
@app.post("/scrape")
async def scrape_web_pages(request: WebScrapeRequest, background_tasks: BackgroundTasks):
    """Scrape web pages and add them to the index"""
    try:
        reader = BeautifulSoupWebReader()
        scraped_docs = reader.load_data(urls=request.urls)
        
        # Add metadata
        for i, doc in enumerate(scraped_docs):
            doc.metadata.update({
                "source": "web_scraping",
                "url": request.urls[i] if i < len(request.urls) else "unknown",
                "scraped_at": datetime.now().isoformat()
            })
        
        documents.extend(scraped_docs)
        create_index_from_documents(documents)
        
        return {
            "message": f"Scraped {len(scraped_docs)} documents successfully",
            "total_documents": len(documents),
            "scraped_urls": request.urls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping web pages: {str(e)}")

# List documents endpoint
@app.get("/documents")
async def list_documents():
    """List all documents in the index"""
    try:
        doc_list = []
        for i, doc in enumerate(documents):
            doc_list.append({
                "id": i,
                "text_preview": doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                "metadata": doc.metadata,
                "length": len(doc.text)
            })
        
        return doc_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

# Clear documents endpoint
@app.delete("/documents")
async def clear_documents():
    """Clear all documents and reset the index"""
    try:
        global documents, index
        documents = []
        index = None
        
        return {"message": "All documents cleared and index reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

