"""
Security utilities for RAG Agent Platform.
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
import time

# Try to import redis, but make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

security = HTTPBearer(auto_error=False)

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

# Rate limiting configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests per window
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# In-memory rate limit store (fallback if Redis not available)
_memory_rate_limits: Dict[str, Dict[str, int]] = {}


class SecurityConfig:
    """Security configuration."""
    
    def __init__(self):
        self.jwt_secret = JWT_SECRET
        self.jwt_algorithm = JWT_ALGORITHM
        self.jwt_expiration_hours = JWT_EXPIRATION_HOURS
        self.rate_limit_enabled = RATE_LIMIT_ENABLED
        self.rate_limit_requests = RATE_LIMIT_REQUESTS
        self.rate_limit_window = RATE_LIMIT_WINDOW
        
        # Redis client (optional)
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", "6379"))
                redis_db = int(os.getenv("REDIS_DB", "0"))
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
            except Exception:
                self.redis_client = None


# Global security config
security_config = SecurityConfig()


def create_jwt_token(user_id: str, email: Optional[str] = None, expires_in_hours: Optional[int] = None) -> str:
    """Create a JWT token."""
    expiration = expires_in_hours or security_config.jwt_expiration_hours
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=expiration),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, security_config.jwt_secret, algorithm=security_config.jwt_algorithm)


def verify_jwt_token(token: str) -> Dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, security_config.jwt_secret, algorithms=[security_config.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict:
    """Get current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    return verify_jwt_token(token)


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict]:
    """Get current user if authenticated, otherwise return None."""
    try:
        if credentials:
            token = credentials.credentials
            return verify_jwt_token(token)
    except HTTPException:
        pass
    return None


def rate_limit_key(identifier: str, endpoint: str) -> str:
    """Generate rate limit key."""
    return f"rate_limit:{identifier}:{endpoint}"


def check_rate_limit(identifier: str, endpoint: str = "default"):
    """Check rate limit for identifier (user_id or IP)."""
    if not security_config.rate_limit_enabled:
        return
    
    key = rate_limit_key(identifier, endpoint)
    current_time = int(time.time())
    window_start = current_time // security_config.rate_limit_window
    
    # Try Redis first
    if security_config.redis_client:
        try:
            redis_key = f"{key}:{window_start}"
            current = security_config.redis_client.get(redis_key)
            
            if current and int(current) >= security_config.rate_limit_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {security_config.rate_limit_requests} requests per {security_config.rate_limit_window} seconds."
                )
            
            # Increment counter
            pipe = security_config.redis_client.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, security_config.rate_limit_window)
            pipe.execute()
            return
        except Exception:
            # Fall back to memory if Redis fails
            pass
    
    # Fallback to in-memory storage
    if key not in _memory_rate_limits:
        _memory_rate_limits[key] = {}
    
    window_key = str(window_start)
    if window_key not in _memory_rate_limits[key]:
        _memory_rate_limits[key][window_key] = 0
    
    _memory_rate_limits[key][window_key] += 1
    
    # Clean old windows (simple cleanup)
    if len(_memory_rate_limits[key]) > 2:
        oldest = min(_memory_rate_limits[key].keys())
        del _memory_rate_limits[key][oldest]
    
    if _memory_rate_limits[key][window_key] >= security_config.rate_limit_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {security_config.rate_limit_requests} requests per {security_config.rate_limit_window} seconds."
        )


def rate_limit_middleware(endpoint: str = "default"):
    """Decorator for rate limiting."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get user_id from request, fallback to IP
            identifier = "anonymous"
            
            # Check if user is authenticated
            request = kwargs.get('request')
            if request:
                # Try to get user from auth
                auth_header = request.headers.get("Authorization", "")
                if auth_header.startswith("Bearer "):
                    try:
                        token = auth_header.split(" ")[1]
                        payload = verify_jwt_token(token)
                        identifier = payload.get("user_id", "anonymous")
                    except HTTPException:
                        pass
                
                # Fallback to IP
                if identifier == "anonymous":
                    client_host = getattr(request, "client", None)
                    if client_host:
                        identifier = f"ip:{client_host.host}"
            
            check_rate_limit(identifier, endpoint)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def get_client_ip(request) -> str:
    """Get client IP from request."""
    if hasattr(request, "client") and request.client:
        return request.client.host
    return "unknown"


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize user input."""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Trim whitespace
    text = text.strip()
    
    # Check length
    if max_length and len(text) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")
    
    return text


def validate_query(query: str) -> str:
    """Validate and sanitize query input."""
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    max_query_length = int(os.getenv("MAX_QUERY_LENGTH", "2000"))
    return sanitize_input(query, max_length=max_query_length)


def validate_document_text(text: str) -> str:
    """Validate and sanitize document text."""
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text cannot be empty"
        )
    
    max_document_length = int(os.getenv("MAX_DOCUMENT_LENGTH", "100000"))
    return sanitize_input(text, max_length=max_document_length)

