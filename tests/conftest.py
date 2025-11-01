"""
Test configuration and fixtures for RAG Agent Platform.
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_openai_key(monkeypatch):
    """Mock OpenAI API key for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    yield "test-key-123"


@pytest.fixture
def mock_settings():
    """Mock LlamaIndex Settings."""
    with patch('src.rag_agent.api_server.Settings') as mock_settings:
        yield mock_settings


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        "RAG (Retrieval-Augmented Generation) is a technique that combines retrieval with generation.",
        "LlamaIndex is a data framework for LLM applications.",
        "OpenAI provides powerful language models like GPT-3.5 and GPT-4."
    ]


@pytest.fixture
def sample_query():
    """Sample query for testing."""
    return "What is RAG?"


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = MagicMock()
    mock.complete.return_value = "Mock response"
    return mock


@pytest.fixture
def mock_embed_model():
    """Mock embedding model for testing."""
    mock = MagicMock()
    mock.get_query_embedding.return_value = [0.1] * 1536
    mock.get_text_embeddings.return_value = [[0.1] * 1536]
    return mock


@pytest.fixture
def mock_vector_index():
    """Mock vector index for testing."""
    mock = MagicMock()
    mock_query_engine = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mock answer"
    mock_response.source_nodes = []
    mock_query_engine.query.return_value = mock_response
    mock.as_query_engine.return_value = mock_query_engine
    return mock


@pytest.fixture
def mock_agent():
    """Mock agent for testing."""
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.__str__ = lambda x: "Agent response"
    mock.chat.return_value = mock_response
    mock.memory = MagicMock()
    mock.memory.reset = MagicMock()
    return mock


@pytest.fixture
def client():
    """Create test client for FastAPI."""
    # We'll patch the imports to avoid actual initialization
    with patch('src.rag_agent.api_server.setup_llamaindex'), \
         patch('src.rag_agent.api_server.index', None), \
         patch('src.rag_agent.api_server.agent', None):
        from src.rag_agent.api_server import app
        client = TestClient(app)
        yield client


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test."""
    yield
    # Cleanup if needed
