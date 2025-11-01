from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import json
import time
import hashlib
import uuid
from datetime import datetime, timedelta
import redis
import jwt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RAG API Service",
    description="Enterprise-grade RAG API for document processing and Q&A",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Redis for rate limiting and caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# In-memory storage (replace with database in production)
users_db = {}
api_keys_db = {}
usage_db = {}
knowledge_bases_db = {}

# Pricing tiers
PRICING_TIERS = {
    "free": {"queries_per_month": 1000, "documents": 100, "price": 0},
    "starter": {"queries_per_month": 10000, "documents": 1000, "price": 49},
    "growth": {"queries_per_month": 100000, "documents": 10000, "price": 199},
    "scale": {"queries_per_month": 1000000, "documents": 100000, "price": 499},
    "enterprise": {"queries_per_month": -1, "documents": -1, "price": "custom"}
}

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    company: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class APIKeyCreate(BaseModel):
    name: str
    tier: str = "free"

class DocumentUpload(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = {}
    knowledge_base_id: Optional[str] = None

class QueryRequest(BaseModel):
    question: str
    knowledge_base_id: Optional[str] = None
    max_results: int = 5

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None

class UsageResponse(BaseModel):
    user_id: str
    tier: str
    queries_used: int
    queries_limit: int
    documents_used: int
    documents_limit: int
    reset_date: datetime

# Authentication functions
def create_jwt_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET", "secret"), algorithm="HS256")

def verify_jwt_token(token: str) -> str:
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET", "secret"), algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    return verify_jwt_token(token)

def get_api_key_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    api_key = credentials.credentials
    if api_key not in api_keys_db:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_keys_db[api_key]["user_id"]

# Rate limiting
def check_rate_limit(user_id: str, endpoint: str):
    key = f"rate_limit:{user_id}:{endpoint}"
    current = redis_client.get(key)
    
    if current and int(current) > 100:  # 100 requests per minute
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, 60)  # 1 minute window
    pipe.execute()

# Usage tracking
def track_usage(user_id: str, operation: str, count: int = 1):
    month_key = datetime.now().strftime("%Y-%m")
    usage_key = f"usage:{user_id}:{month_key}"
    
    current_usage = redis_client.hgetall(usage_key)
    if not current_usage:
        current_usage = {"queries": "0", "documents": "0"}
    
    if operation == "query":
        new_count = int(current_usage.get("queries", 0)) + count
        redis_client.hset(usage_key, "queries", new_count)
    elif operation == "document":
        new_count = int(current_usage.get("documents", 0)) + count
        redis_client.hset(usage_key, "documents", new_count)
    
    redis_client.expire(usage_key, 60 * 60 * 24 * 90)  # 90 days

def check_usage_limits(user_id: str, operation: str):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tier = user.get("tier", "free")
    limits = PRICING_TIERS[tier]
    
    month_key = datetime.now().strftime("%Y-%m")
    usage_key = f"usage:{user_id}:{month_key}"
    current_usage = redis_client.hgetall(usage_key)
    
    if operation == "query":
        used = int(current_usage.get("queries", 0))
        limit = limits["queries_per_month"]
    else:
        used = int(current_usage.get("documents", 0))
        limit = limits["documents"]
    
    if limit != -1 and used >= limit:
        raise HTTPException(status_code=429, detail=f"{operation} limit exceeded")

# API Endpoints

@app.post("/auth/register", response_model=Dict[str, Any])
async def register_user(user_data: UserCreate):
    """Register a new user"""
    if user_data.email in [u["email"] for u in users_db.values()]:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
    
    users_db[user_id] = {
        "email": user_data.email,
        "password": hashed_password,
        "company": user_data.company,
        "tier": "free",
        "created_at": datetime.now().isoformat()
    }
    
    token = create_jwt_token(user_id)
    return {"user_id": user_id, "token": token, "tier": "free"}

@app.post("/auth/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin):
    """Login user and return JWT token"""
    for user_id, user in users_db.items():
        if user["email"] == login_data.email:
            hashed_password = hashlib.sha256(login_data.password.encode()).hexdigest()
            if user["password"] == hashed_password:
                token = create_jwt_token(user_id)
                return {"user_id": user_id, "token": token, "tier": user["tier"]}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/api-keys", response_model=Dict[str, Any])
async def create_api_key(api_key_data: APIKeyCreate, user_id: str = Depends(get_current_user)):
    """Create a new API key for the user"""
    api_key = f"rag_{uuid.uuid4().hex}"
    api_keys_db[api_key] = {
        "user_id": user_id,
        "name": api_key_data.name,
        "created_at": datetime.now().isoformat()
    }
    
    return {"api_key": api_key, "name": api_key_data.name}

@app.get("/auth/api-keys", response_model=List[Dict[str, Any]])
async def list_api_keys(user_id: str = Depends(get_current_user)):
    """List all API keys for the user"""
    keys = []
    for key, data in api_keys_db.items():
        if data["user_id"] == user_id:
            keys.append({
                "name": data["name"],
                "created_at": data["created_at"],
                "last_used": data.get("last_used")
            })
    return keys

@app.get("/usage", response_model=UsageResponse)
async def get_usage(user_id: str = Depends(get_current_user)):
    """Get current usage statistics"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tier = user.get("tier", "free")
    limits = PRICING_TIERS[tier]
    
    month_key = datetime.now().strftime("%Y-%m")
    usage_key = f"usage:{user_id}:{month_key}"
    current_usage = redis_client.hgetall(usage_key)
    
    # Calculate reset date (first day of next month)
    now = datetime.now()
    if now.month == 12:
        reset_date = datetime(now.year + 1, 1, 1)
    else:
        reset_date = datetime(now.year, now.month + 1, 1)
    
    return UsageResponse(
        user_id=user_id,
        tier=tier,
        queries_used=int(current_usage.get("queries", 0)),
        queries_limit=limits["queries_per_month"],
        documents_used=int(current_usage.get("documents", 0)),
        documents_limit=limits["documents"],
        reset_date=reset_date
    )

@app.post("/knowledge-bases", response_model=Dict[str, Any])
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate, 
    user_id: str = Depends(get_current_user)
):
    """Create a new knowledge base"""
    kb_id = str(uuid.uuid4())
    knowledge_bases_db[kb_id] = {
        "user_id": user_id,
        "name": kb_data.name,
        "description": kb_data.description,
        "created_at": datetime.now().isoformat(),
        "document_count": 0
    }
    
    return {"knowledge_base_id": kb_id, "name": kb_data.name}

@app.get("/knowledge-bases", response_model=List[Dict[str, Any]])
async def list_knowledge_bases(user_id: str = Depends(get_current_user)):
    """List all knowledge bases for the user"""
    kbs = []
    for kb_id, kb in knowledge_bases_db.items():
        if kb["user_id"] == user_id:
            kbs.append({
                "id": kb_id,
                "name": kb["name"],
                "description": kb["description"],
                "document_count": kb["document_count"],
                "created_at": kb["created_at"]
            })
    return kbs

@app.post("/documents", response_model=Dict[str, Any])
async def add_document(
    document: DocumentUpload,
    user_id: str = Depends(get_current_user)
):
    """Add a document to the knowledge base"""
    check_rate_limit(user_id, "documents")
    check_usage_limits(user_id, "document")
    
    # Here you would integrate with your existing LlamaIndex setup
    # For now, we'll just track usage
    
    track_usage(user_id, "document", 1)
    
    # Update knowledge base document count
    if document.knowledge_base_id and document.knowledge_base_id in knowledge_bases_db:
        knowledge_bases_db[document.knowledge_base_id]["document_count"] += 1
    
    return {
        "message": "Document added successfully",
        "document_id": str(uuid.uuid4()),
        "text_length": len(document.text)
    }

@app.post("/query", response_model=Dict[str, Any])
async def query_knowledge_base(
    query: QueryRequest,
    user_id: str = Depends(get_current_user)
):
    """Query the knowledge base"""
    check_rate_limit(user_id, "query")
    check_usage_limits(user_id, "query")
    
    track_usage(user_id, "query", 1)
    
    # Here you would integrate with your existing LlamaIndex setup
    # For now, return a mock response
    
    return {
        "answer": f"This is a mock response to: {query.question}",
        "sources": [
            {
                "text": "Sample source document...",
                "score": 0.95,
                "metadata": {"source": "mock"}
            }
        ],
        "query": query.question,
        "processing_time": 0.5
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 