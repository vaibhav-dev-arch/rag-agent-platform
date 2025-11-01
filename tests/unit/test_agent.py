"""
Unit tests for agent architecture.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestRAGAgent:
    """Test RAGAgent class."""
    
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAI')
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAIEmbedding')
    @patch('src.rag_agent.agent_architecture.advanced_agent.Settings')
    def test_agent_initialization(self, mock_settings, mock_embed, mock_llm):
        """Test agent initialization."""
        from src.rag_agent.agent_architecture.advanced_agent import RAGAgent
        
        mock_llm.return_value = MagicMock()
        mock_embed.return_value = MagicMock()
        
        agent = RAGAgent()
        
        assert agent is not None
        assert hasattr(agent, 'tools')
        assert hasattr(agent, 'agent')
    
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAI')
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAIEmbedding')
    @patch('src.rag_agent.agent_architecture.advanced_agent.Settings')
    def test_agent_query(self, mock_settings, mock_embed, mock_llm):
        """Test agent query."""
        from src.rag_agent.agent_architecture.advanced_agent import RAGAgent
        
        mock_llm.return_value = MagicMock()
        mock_embed.return_value = MagicMock()
        
        agent = RAGAgent()
        mock_response = MagicMock()
        mock_response.__str__ = lambda x: "Test response"
        agent.agent.chat = MagicMock(return_value=mock_response)
        
        response = agent.query("test query")
        
        assert response is not None
        agent.agent.chat.assert_called_once()
    
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAI')
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAIEmbedding')
    @patch('src.rag_agent.agent_architecture.advanced_agent.Settings')
    def test_agent_tools(self, mock_settings, mock_embed, mock_llm):
        """Test agent tools."""
        from src.rag_agent.agent_architecture.advanced_agent import RAGAgent
        
        mock_llm.return_value = MagicMock()
        mock_embed.return_value = MagicMock()
        
        agent = RAGAgent()
        
        assert len(agent.tools) > 0
        tool_names = [tool.metadata.name for tool in agent.tools]
        assert "document_search" in tool_names
        assert "web_search" in tool_names


class TestAgentTools:
    """Test agent tools."""
    
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAI')
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAIEmbedding')
    @patch('src.rag_agent.agent_architecture.advanced_agent.Settings')
    def test_document_search_tool(self, mock_settings, mock_embed, mock_llm):
        """Test document search tool."""
        from src.rag_agent.agent_architecture.advanced_agent import RAGAgent
        
        mock_llm.return_value = MagicMock()
        mock_embed.return_value = MagicMock()
        
        agent = RAGAgent()
        
        # Mock the index
        with patch.object(agent, 'index', MagicMock()) as mock_index:
            mock_query_engine = MagicMock()
            mock_response = MagicMock()
            mock_response.__str__ = lambda x: "Test answer"
            mock_query_engine.query.return_value = mock_response
            mock_index.as_query_engine.return_value = mock_query_engine
            
            result = agent.document_search("test query")
            
            assert result is not None
    
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAI')
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAIEmbedding')
    @patch('src.rag_agent.agent_architecture.advanced_agent.Settings')
    def test_web_search_tool(self, mock_settings, mock_embed, mock_llm):
        """Test web search tool."""
        from src.rag_agent.agent_architecture.advanced_agent import RAGAgent
        
        mock_llm.return_value = MagicMock()
        mock_embed.return_value = MagicMock()
        
        agent = RAGAgent()
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'items': [{'title': 'Test', 'snippet': 'Test snippet'}]
            }
            mock_get.return_value = mock_response
            
            result = agent.web_search("test query")
            
            assert result is not None
            assert "Test" in result or "test" in result.lower()
    
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAI')
    @patch('src.rag_agent.agent_architecture.advanced_agent.OpenAIEmbedding')
    @patch('src.rag_agent.agent_architecture.advanced_agent.Settings')
    def test_calculate_tool(self, mock_settings, mock_embed, mock_llm):
        """Test calculate tool."""
        from src.rag_agent.agent_architecture.advanced_agent import RAGAgent
        
        mock_llm.return_value = MagicMock()
        mock_embed.return_value = MagicMock()
        
        agent = RAGAgent()
        
        result = agent.calculate("2 + 2")
        
        assert result is not None
        assert "4" in result or "result" in result.lower()

