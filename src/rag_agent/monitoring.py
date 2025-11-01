"""
Monitoring and observability for RAG Agent Platform.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
import json

# Try to import Prometheus client
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = None
    Histogram = None
    Gauge = None

# Try to import Sentry
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None

# Configure logging
logger = logging.getLogger(__name__)

# Prometheus metrics
if PROMETHEUS_AVAILABLE:
    # Request metrics
    http_requests_total = Counter(
        'http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status']
    )
    
    http_request_duration = Histogram(
        'http_request_duration_seconds',
        'HTTP request duration',
        ['method', 'endpoint']
    )
    
    # RAG-specific metrics
    rag_queries_total = Counter(
        'rag_queries_total',
        'Total RAG queries',
        ['status']
    )
    
    rag_query_duration = Histogram(
        'rag_query_duration_seconds',
        'RAG query processing duration'
    )
    
    agent_queries_total = Counter(
        'agent_queries_total',
        'Total agent queries',
        ['status']
    )
    
    agent_query_duration = Histogram(
        'agent_query_duration_seconds',
        'Agent query processing duration'
    )
    
    # System metrics
    active_connections = Gauge(
        'active_connections',
        'Number of active connections'
    )
    
    documents_indexed = Gauge(
        'documents_indexed',
        'Number of documents in index'
    )
    
    vector_index_size = Gauge(
        'vector_index_size',
        'Size of vector index'
    )
    
    # Rate limiting metrics
    rate_limit_hits = Counter(
        'rate_limit_hits_total',
        'Total rate limit hits',
        ['endpoint', 'identifier']
    )
    
    # Database metrics
    db_queries_total = Counter(
        'db_queries_total',
        'Total database queries',
        ['operation', 'status']
    )
    
    db_query_duration = Histogram(
        'db_query_duration_seconds',
        'Database query duration',
        ['operation']
    )
else:
    # Dummy metrics if Prometheus not available
    http_requests_total = None
    http_request_duration = None
    rag_queries_total = None
    rag_query_duration = None
    agent_queries_total = None
    agent_query_duration = None
    active_connections = None
    documents_indexed = None
    vector_index_size = None
    rate_limit_hits = None
    db_queries_total = None
    db_query_duration = None


def init_monitoring(sentry_dsn: Optional[str] = None, environment: str = "production"):
    """Initialize monitoring infrastructure."""
    # Initialize Sentry for error tracking
    if SENTRY_AVAILABLE and sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% of transactions
            profiles_sample_rate=0.1,
        )
        logger.info("✅ Sentry initialized for error tracking")
    
    if PROMETHEUS_AVAILABLE:
        logger.info("✅ Prometheus metrics initialized")
    
    logger.info("✅ Monitoring infrastructure initialized")


def track_request(method: str, endpoint: str, status: int, duration: float):
    """Track HTTP request metrics."""
    if http_requests_total:
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    
    if http_request_duration:
        http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)


def track_rag_query(status: str, duration: float):
    """Track RAG query metrics."""
    if rag_queries_total:
        rag_queries_total.labels(status=status).inc()
    
    if rag_query_duration:
        rag_query_duration.observe(duration)


def track_agent_query(status: str, duration: float):
    """Track agent query metrics."""
    if agent_queries_total:
        agent_queries_total.labels(status=status).inc()
    
    if agent_query_duration:
        agent_query_duration.observe(duration)


def track_rate_limit(endpoint: str, identifier: str):
    """Track rate limit hits."""
    if rate_limit_hits:
        rate_limit_hits.labels(endpoint=endpoint, identifier=identifier).inc()


def track_db_query(operation: str, status: str, duration: float):
    """Track database query metrics."""
    if db_queries_total:
        db_queries_total.labels(operation=operation, status=status).inc()
    
    if db_query_duration:
        db_query_duration.labels(operation=operation).observe(duration)


def update_documents_count(count: int):
    """Update documents count gauge."""
    if documents_indexed:
        documents_indexed.set(count)


def update_vector_index_size(size: int):
    """Update vector index size gauge."""
    if vector_index_size:
        vector_index_size.set(size)


def update_active_connections(count: int):
    """Update active connections gauge."""
    if active_connections:
        active_connections.set(count)


def get_metrics():
    """Get Prometheus metrics."""
    if PROMETHEUS_AVAILABLE:
        return generate_latest()
    return b"# Prometheus client not available\n"


def request_timing_middleware(func):
    """Decorator to track request timing."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        status = 200
        
        try:
            response = await func(*args, **kwargs)
            if hasattr(response, 'status_code'):
                status = response.status_code
            return response
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            # Extract method and endpoint from request if available
            method = "UNKNOWN"
            endpoint = "UNKNOWN"
            
            request = kwargs.get('request') or kwargs.get('req')
            if request:
                method = request.method
                endpoint = request.url.path
            
            track_request(method, endpoint, status, duration)
    
    return wrapper


def structured_log(level: str, message: str, **kwargs):
    """Create structured log entry."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    
    log_message = json.dumps(log_entry)
    
    if level == "DEBUG":
        logger.debug(log_message)
    elif level == "INFO":
        logger.info(log_message)
    elif level == "WARNING":
        logger.warning(log_message)
    elif level == "ERROR":
        logger.error(log_message)
    elif level == "CRITICAL":
        logger.critical(log_message)
    else:
        logger.info(log_message)


class PerformanceMonitor:
    """Monitor performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "start_time": datetime.utcnow().isoformat(),
            "requests": 0,
            "errors": 0,
            "avg_response_time": 0.0,
            "total_response_time": 0.0
        }
    
    def record_request(self, duration: float, success: bool = True):
        """Record a request."""
        self.metrics["requests"] += 1
        self.metrics["total_response_time"] += duration
        
        if not success:
            self.metrics["errors"] += 1
        
        # Calculate average
        if self.metrics["requests"] > 0:
            self.metrics["avg_response_time"] = (
                self.metrics["total_response_time"] / self.metrics["requests"]
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        uptime = (datetime.utcnow() - datetime.fromisoformat(self.metrics["start_time"])).total_seconds()
        
        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "error_rate": (
                self.metrics["errors"] / self.metrics["requests"]
                if self.metrics["requests"] > 0
                else 0.0
            )
        }


# Global performance monitor
performance_monitor = PerformanceMonitor()

