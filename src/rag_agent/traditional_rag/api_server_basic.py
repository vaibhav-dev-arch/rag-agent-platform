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
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LlamaIndex RAG API",
    description="A REST API for Retrieval-Augmented Generation using LlamaIndex and OpenAI",
    version="1.0.0"
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

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask")
    include_sources: bool = Field(True, description="Whether to include source information")

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    query: str
    processing_time: float

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
    message: str

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

def create_index_from_documents(docs: List[Document]):
    """Create a vector index from documents"""
    global index
    
    if not docs:
        raise HTTPException(status_code=400, detail="No documents provided")
    
    parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
    nodes = parser.get_nodes_from_documents(docs)
    index = VectorStoreIndex(nodes)
    
    return len(nodes)

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    try:
        setup_llamaindex()
        print("✅ LlamaIndex configured successfully")
    except Exception as e:
        print(f"❌ Error during startup: {e}")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LlamaIndex RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    openai_configured = os.getenv("OPENAI_API_KEY") is not None
    index_ready = index is not None
    
    status = "healthy" if openai_configured and index_ready else "degraded"
    message = "API is ready" if status == "healthy" else "API needs configuration"
    
    return HealthResponse(
        status=status,
        openai_configured=openai_configured,
        index_ready=index_ready,
        message=message
    )

@app.get("/status", response_model=IndexStatus)
async def get_index_status():
    """Get current index status"""
    return IndexStatus(
        has_index=index is not None,
        document_count=len(documents),
        node_count=len(index.nodes) if index else 0,
        is_configured=os.getenv("OPENAI_API_KEY") is not None
    )

@app.post("/documents", response_model=Dict[str, Any])
async def add_document(request: DocumentRequest):
    """Add a single document to the index"""
    global documents, index
    
    try:
        # Create document
        doc = Document(text=request.text, metadata=request.metadata or {})
        documents.append(doc)
        
        # Recreate index with all documents
        if documents:
            node_count = create_index_from_documents(documents)
            return {
                "message": "Document added successfully",
                "document_count": len(documents),
                "node_count": node_count,
                "document_id": len(documents) - 1
            }
        else:
            return {"message": "Document added but no index created (no documents)"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

@app.post("/documents/batch", response_model=Dict[str, Any])
async def add_documents_batch(requests: List[DocumentRequest]):
    """Add multiple documents to the index"""
    global documents, index
    
    try:
        # Create documents
        new_docs = [
            Document(text=req.text, metadata=req.metadata or {})
            for req in requests
        ]
        documents.extend(new_docs)
        
        # Recreate index with all documents
        if documents:
            node_count = create_index_from_documents(documents)
            return {
                "message": f"Added {len(new_docs)} documents successfully",
                "total_documents": len(documents),
                "node_count": node_count
            }
        else:
            return {"message": "Documents added but no index created (no documents)"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding documents: {str(e)}")

@app.post("/scrape", response_model=Dict[str, Any])
async def scrape_web_pages(request: WebScrapeRequest):
    """Scrape web pages and add to index"""
    global documents, index
    
    try:
        reader = BeautifulSoupWebReader()
        scraped_docs = reader.load_data(urls=request.urls)
        
        # Add scraped documents
        documents.extend(scraped_docs)
        
        # Recreate index with all documents
        if documents:
            node_count = create_index_from_documents(documents)
            return {
                "message": f"Successfully scraped {len(scraped_docs)} documents",
                "scraped_count": len(scraped_docs),
                "total_documents": len(documents),
                "node_count": node_count
            }
        else:
            return {"message": "Scraped documents but no index created (no documents)"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping web pages: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_index(request: QueryRequest):
    """Query the index with a question"""
    import time
    
    if not index:
        raise HTTPException(status_code=400, detail="No index available. Please add documents first.")
    
    start_time = time.time()
    
    try:
        query_engine = index.as_query_engine()
        response = query_engine.query(request.query)
        
        processing_time = time.time() - start_time
        
        # Prepare sources if requested
        sources = []
        if request.include_sources and response.source_nodes:
            for i, source_node in enumerate(response.source_nodes):
                sources.append({
                    "id": i,
                    "score": source_node.score,
                    "text": source_node.text[:500] + "..." if len(source_node.text) > 500 else source_node.text,
                    "metadata": source_node.metadata
                })
        
        return QueryResponse(
            answer=str(response),
            sources=sources,
            query=request.query,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.delete("/documents")
async def clear_documents():
    """Clear all documents and reset the index"""
    global documents, index
    
    documents = []
    index = None
    
    return {"message": "All documents cleared and index reset"}

@app.get("/documents", response_model=List[Dict[str, Any]])
async def list_documents():
    """List all documents in the index"""
    return [
        {
            "id": i,
            "text_preview": doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
            "metadata": doc.metadata,
            "length": len(doc.text)
        }
        for i, doc in enumerate(documents)
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 