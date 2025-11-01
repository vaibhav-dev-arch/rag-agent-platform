"""
Integration tests for API endpoints.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestAPIWorkflows:
    """Test complete API workflows."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('src.rag_agent.api_server.setup_llamaindex'), \
             patch('src.rag_agent.api_server.index', None), \
             patch('src.rag_agent.api_server.agent', None):
            from src.rag_agent.api_server import app
            return TestClient(app)
    
    def test_complete_document_workflow(self, client):
        """Test complete document add and query workflow."""
        # Add document
        response = client.post("/documents/add", json={
            "text": "RAG is a powerful technique",
            "metadata": {"title": "RAG Guide"}
        })
        assert response.status_code == 200
        
        # Check status
        response = client.get("/documents/status")
        assert response.status_code == 200
        data = response.json()
        assert data["has_index"] is True
        assert data["document_count"] > 0
    
    def test_health_to_query_workflow(self, client):
        """Test health check to query workflow."""
        # Health check
        response = client.get("/health")
        assert response.status_code == 200
        
        # System info
        response = client.get("/system/info")
        assert response.status_code == 200
        
        # Query (should fail without documents)
        response = client.post("/query", json={"query": "test"})
        # Can be 400 (no index) or 200 (with mocked index)
        assert response.status_code in [200, 400]
    
    def test_agent_tools_endpoint(self, client):
        """Test agent tools endpoint."""
        response = client.get("/agent/tools")
        assert response.status_code == 200
        data = response.json()
        assert "available_tools" in data
        assert "tool_descriptions" in data
        assert len(data["available_tools"]) > 0


class TestErrorHandlingIntegration:
    """Test error handling in integration scenarios."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('src.rag_agent.api_server.setup_llamaindex'), \
             patch('src.rag_agent.api_server.index', None), \
             patch('src.rag_agent.api_server.agent', None):
            from src.rag_agent.api_server import app
            return TestClient(app)
    
    def test_invalid_query_format(self, client):
        """Test handling of invalid query format."""
        # Missing required field
        response = client.post("/query", json={})
        assert response.status_code == 422  # Validation error
    
    def test_query_without_index(self, client):
        """Test query when index doesn't exist."""
        response = client.post("/query", json={"query": "test"})
        assert response.status_code == 400
        assert "No documents indexed" in response.json()["detail"]

