"""
Unit tests for API server.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        with patch('src.rag_agent.api_server.index', None), \
             patch('src.rag_agent.api_server.agent', None):
            from src.rag_agent.api_server import app
            client = TestClient(app)
            
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "degraded"]
            assert "openai_configured" in data
            assert "index_ready" in data
            assert "agent_ready" in data
    
    def test_system_info_endpoint(self, client):
        """Test system info endpoint."""
        with patch('src.rag_agent.api_server.index', None), \
             patch('src.rag_agent.api_server.agent', None):
            from src.rag_agent.api_server import app
            client = TestClient(app)
            
            response = client.get("/system/info")
            assert response.status_code == 200
            data = response.json()
            assert "version" in data
            assert "python_version" in data


class TestQueryEndpoints:
    """Test query endpoints."""
    
    def test_query_without_index(self, client):
        """Test query when no index exists."""
        with patch('src.rag_agent.api_server.index', None):
            from src.rag_agent.api_server import app
            client = TestClient(app)
            
            response = client.post("/query", json={"query": "test"})
            assert response.status_code == 400
            assert "No documents indexed" in response.json()["detail"]
    
    @patch('src.rag_agent.api_server.index')
    def test_query_with_index(self, mock_index, client):
        """Test query with existing index."""
        # Mock query engine and response
        mock_query_engine = MagicMock()
        mock_response = MagicMock()
        mock_response.__str__ = lambda x: "Test answer"
        mock_response.source_nodes = []
        mock_query_engine.query.return_value = mock_response
        mock_index.as_query_engine.return_value = mock_query_engine
        
        from src.rag_agent.api_server import app
        client = TestClient(app)
        
        response = client.post("/query", json={"query": "test"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "query" in data
        assert "processing_time" in data
        assert data["query"] == "test"
    
    @patch('src.rag_agent.api_server.index')
    def test_query_with_sources(self, mock_index, client):
        """Test query with sources included."""
        # Mock query engine with source nodes
        mock_query_engine = MagicMock()
        mock_response = MagicMock()
        mock_response.__str__ = lambda x: "Test answer"
        
        mock_node = MagicMock()
        mock_node.text = "Sample text" * 50  # Long text to test truncation
        mock_node.score = 0.95
        mock_node.metadata = {"source": "test.pdf"}
        mock_response.source_nodes = [mock_node]
        
        mock_query_engine.query.return_value = mock_response
        mock_index.as_query_engine.return_value = mock_query_engine
        
        from src.rag_agent.api_server import app
        client = TestClient(app)
        
        response = client.post("/query", json={"query": "test", "include_sources": True})
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert len(data["sources"]) > 0


class TestAgentEndpoints:
    """Test agent endpoints."""
    
    def test_agent_query_without_agent(self, client):
        """Test agent query when agent is not initialized."""
        with patch('src.rag_agent.api_server.agent', None):
            from src.rag_agent.api_server import app
            client = TestClient(app)
            
            response = client.post("/agent/query", json={"query": "test"})
            assert response.status_code == 500
            assert "not initialized" in response.json()["detail"]
    
    @patch('src.rag_agent.api_server.agent')
    def test_agent_query_with_agent(self, mock_agent, client):
        """Test agent query with initialized agent."""
        mock_response = MagicMock()
        mock_response.__str__ = lambda x: "Agent answer"
        mock_agent.chat.return_value = mock_response
        mock_agent.memory = MagicMock()
        mock_agent.memory.reset = MagicMock()
        
        from src.rag_agent.api_server import app
        client = TestClient(app)
        
        response = client.post("/agent/query", json={"query": "test"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "tools_used" in data
        assert data["query"] == "test"
    
    def test_agent_tools_endpoint(self, client):
        """Test agent tools endpoint."""
        from src.rag_agent.api_server import app
        client = TestClient(app)
        
        response = client.get("/agent/tools")
        assert response.status_code == 200
        data = response.json()
        assert "available_tools" in data
        assert "tool_descriptions" in data
        assert len(data["available_tools"]) > 0


class TestDocumentEndpoints:
    """Test document management endpoints."""
    
    def test_add_document(self, client, sample_documents):
        """Test adding a document."""
        with patch('src.rag_agent.api_server.VectorStoreIndex') as mock_index_class, \
             patch('src.rag_agent.api_server.Document') as mock_document, \
             patch('src.rag_agent.api_server.Settings') as mock_settings:
            
            mock_index = MagicMock()
            mock_index_class.from_documents.return_value = mock_index
            
            from src.rag_agent.api_server import app
            client = TestClient(app)
            
            response = client.post("/documents/add", json={
                "text": sample_documents[0],
                "metadata": {"title": "Test"}
            })
            assert response.status_code == 200
            data = response.json()
            assert "document_id" in data
            assert "message" in data
    
    def test_get_index_status_without_index(self, client):
        """Test index status when no index exists."""
        with patch('src.rag_agent.api_server.index', None):
            from src.rag_agent.api_server import app
            client = TestClient(app)
            
            response = client.get("/documents/status")
            assert response.status_code == 200
            data = response.json()
            assert data["has_index"] is False
            assert data["document_count"] == 0


class TestErrorHandling:
    """Test error handling."""
    
    @patch('src.rag_agent.api_server.index')
    def test_query_error_handling(self, mock_index, client):
        """Test error handling in query endpoint."""
        mock_index.as_query_engine.side_effect = Exception("Test error")
        
        from src.rag_agent.api_server import app
        client = TestClient(app)
        
        response = client.post("/query", json={"query": "test"})
        assert response.status_code == 500
        assert "Error querying index" in response.json()["detail"]
    
    @patch('src.rag_agent.api_server.agent')
    def test_agent_error_handling(self, mock_agent, client):
        """Test error handling in agent endpoint."""
        mock_agent.chat.side_effect = Exception("Agent error")
        
        from src.rag_agent.api_server import app
        client = TestClient(app)
        
        response = client.post("/agent/query", json={"query": "test"})
        assert response.status_code == 500
        assert "Error in agent query" in response.json()["detail"]

