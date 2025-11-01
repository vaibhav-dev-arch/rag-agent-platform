"""
Database integration for RAG Agent Platform.
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

# Try to import PostgreSQL driver
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

Base = declarative_base()


class DocumentModel(Base):
    """Document metadata model."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    doc_metadata = Column(JSON, default={})  # Renamed from 'metadata' (reserved in SQLAlchemy)
    source = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed = Column(Boolean, default=False)
    index_id = Column(String(255), nullable=True)


class QueryHistoryModel(Base):
    """Query history model."""
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text)
    user_id = Column(String(255), nullable=True)
    processing_time = Column(Integer)  # milliseconds
    sources_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Database manager for RAG Agent Platform."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager."""
        if database_url:
            self.database_url = database_url
        else:
            # Default to SQLite for local development
            db_path = os.getenv("DATABASE_PATH", "data/rag_platform.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.database_url = f"sqlite:///{db_path}"
        
        # Create engine
        if "sqlite" in self.database_url:
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            self.engine = create_engine(self.database_url)
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Get database session context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None, 
                     source: Optional[str] = None) -> int:
        """Add document to database."""
        with self.get_session() as session:
            doc = DocumentModel(
                text=text,
                doc_metadata=metadata or {},
                source=source,
                indexed=False
            )
            session.add(doc)
            session.flush()
            doc_id = doc.id
            return doc_id
    
    def get_document(self, doc_id: int) -> Optional[DocumentModel]:
        """Get document by ID."""
        with self.get_session() as session:
            return session.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
    
    def get_all_documents(self, limit: int = 100, offset: int = 0) -> List[DocumentModel]:
        """Get all documents."""
        with self.get_session() as session:
            return session.query(DocumentModel).offset(offset).limit(limit).all()
    
    def mark_document_indexed(self, doc_id: int, index_id: Optional[str] = None):
        """Mark document as indexed."""
        with self.get_session() as session:
            doc = session.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
            if doc:
                doc.indexed = True
                doc.index_id = index_id
    
    def add_query_history(self, query: str, response: Optional[str] = None,
                         user_id: Optional[str] = None, processing_time: Optional[int] = None,
                         sources_count: int = 0):
        """Add query to history."""
        with self.get_session() as session:
            history = QueryHistoryModel(
                query=query,
                response=response,
                user_id=user_id,
                processing_time=processing_time,
                sources_count=sources_count
            )
            session.add(history)
            session.flush()
            return history.id
    
    def get_query_history(self, user_id: Optional[str] = None, limit: int = 50) -> List[QueryHistoryModel]:
        """Get query history."""
        with self.get_session() as session:
            query = session.query(QueryHistoryModel)
            if user_id:
                query = query.filter(QueryHistoryModel.user_id == user_id)
            return query.order_by(QueryHistoryModel.created_at.desc()).limit(limit).all()
    
    def delete_document(self, doc_id: int):
        """Delete document."""
        with self.get_session() as session:
            doc = session.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
            if doc:
                session.delete(doc)
    
    def clear_all_documents(self):
        """Clear all documents."""
        with self.get_session() as session:
            session.query(DocumentModel).delete()
            session.query(QueryHistoryModel).delete()


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """Get database manager instance."""
    global _db_manager
    if _db_manager is None:
        database_url = os.getenv("DATABASE_URL")
        _db_manager = DatabaseManager(database_url)
    return _db_manager


def init_database(database_url: Optional[str] = None):
    """Initialize database."""
    global _db_manager
    _db_manager = DatabaseManager(database_url)
    return _db_manager

