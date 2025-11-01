import os
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    """Initialize the application on startup"""
    try:
        setup_llamaindex()
        create_agent()
        print("✅ LlamaIndex and Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error during startup: {str(e)}")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health and configuration status of the API"""
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    index_ready = index is not None
    agent_ready = agent is not None
    
    status = "healthy" if all([openai_configured, index_ready, agent_ready]) else "degraded"
    message = "API is ready" if status == "healthy" else "Some components are not ready"
    
    return HealthResponse(
        status=status,
        openai_configured=openai_configured,
        index_ready=index_ready,
        agent_ready=agent_ready,
        message=message
    )

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
async def query_index(request: QueryRequest):
    """Query the vector index with a question"""
    if index is None:
        raise HTTPException(status_code=400, detail="No documents indexed yet. Please add documents first.")
    
    start_time = time.time()
    
    try:
        query_engine = index.as_query_engine()
        response = query_engine.query(request.query)
        
        processing_time = time.time() - start_time
        
        # Extract sources if requested
        sources = []
        if request.include_sources and hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                sources.append({
                    "text": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                    "score": node.score,
                    "metadata": node.metadata
                })
        
        return QueryResponse(
            answer=str(response),
            sources=sources,
            query=request.query,
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying index: {str(e)}")

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
async def add_document(request: DocumentRequest):
    """Add a document to the index"""
    try:
        doc = Document(
            text=request.text,
            metadata=request.metadata or {}
        )
        
        documents.append(doc)
        create_index_from_documents(documents)
        
        return {
            "message": "Document added successfully",
            "document_count": len(documents),
            "document_id": len(documents) - 1
        }
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

