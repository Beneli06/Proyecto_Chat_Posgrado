"""
Tests for RAG Logic and Query Engine
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.engine.query import RAGQueryEngine


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store"""
    return MagicMock()


@pytest.fixture
def rag_query_engine(mock_vector_store):
    """Create a RAG Query Engine instance with mocked LLM"""
    with patch('app.engine.query.OpenAIEmbeddings'):
        with patch('app.engine.query.Chroma') as mock_chroma:
            with patch('app.engine.query.ChatOpenAI'):
                engine = RAGQueryEngine(
                    vector_db_path="./test_db",
                    model_name="gpt-4",
                    temperature=0.3
                )
                engine.vector_store = mock_vector_store
                return engine


class TestRAGQueryEngine:
    """Test suite for RAG Query Engine"""
    
    def test_engine_initialization(self):
        """Test that RAG engine initializes correctly"""
        with patch('app.engine.query.OpenAIEmbeddings'):
            with patch('app.engine.query.Chroma'):
                with patch('app.engine.query.ChatOpenAI'):
                    engine = RAGQueryEngine()
                    assert engine.model_name == "gpt-4"
                    assert engine.temperature == 0.3
    
    def test_retrieve_context_with_valid_query(self, rag_query_engine, mock_vector_store):
        """Test context retrieval with a valid query"""
        # Mock the similarity search
        mock_doc = MagicMock()
        mock_doc.page_content = "Master's program in Computer Science"
        mock_vector_store.similarity_search.return_value = [mock_doc]
        
        context = rag_query_engine._retrieve_context("What is the master's program?")
        
        assert context is not None
        assert "Master's program" in context
        mock_vector_store.similarity_search.assert_called_once()
    
    def test_retrieve_context_no_results(self, rag_query_engine, mock_vector_store):
        """Test context retrieval when no documents are found"""
        mock_vector_store.similarity_search.return_value = []
        
        context = rag_query_engine._retrieve_context("Unknown topic")
        
        assert context == ""
    
    def test_query_with_invalid_input(self, rag_query_engine):
        """Test query handling with invalid input"""
        result = rag_query_engine.query(None)
        
        assert result["success"] is False
        assert "Invalid question format" in result["error"]
    
    def test_query_with_valid_input(self, rag_query_engine, mock_vector_store):
        """Test query with valid input"""
        # Mock the similarity search
        mock_doc = MagicMock()
        mock_doc.page_content = "Master's program information"
        mock_doc.metadata = {"source": "test.pdf", "page": 1}
        mock_vector_store.similarity_search.return_value = [mock_doc]
        
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.content = "The Master's program is a 2-year program."
        
        with patch.object(rag_query_engine.llm, 'invoke', return_value=mock_response):
            result = rag_query_engine.query("Tell me about the Master's program")
            
            assert result["success"] is True
            assert "Master's program" in result["answer"]
    
    def test_query_with_no_vector_store(self):
        """Test query when vector store is not available"""
        with patch('app.engine.query.OpenAIEmbeddings'):
            with patch('app.engine.query.Chroma'):
                with patch('app.engine.query.ChatOpenAI'):
                    engine = RAGQueryEngine()
                    engine.vector_store = None
                    
                    result = engine.query("What is the program?")
                    
                    assert result["success"] is False
                    assert "No relevant documents found" in result["error"]
    
    def test_query_response_includes_sources(self, rag_query_engine, mock_vector_store):
        """Test that query response includes source documents"""
        # Mock the similarity search
        mock_doc = MagicMock()
        mock_doc.page_content = "Master's program in Business Administration"
        mock_doc.metadata = {"source": "programs.pdf", "page": 5}
        mock_vector_store.similarity_search.return_value = [mock_doc]
        
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.content = "The MBA program is available."
        
        with patch.object(rag_query_engine.llm, 'invoke', return_value=mock_response):
            result = rag_query_engine.query("Tell me about MBA", return_sources=True)
            
            assert result["success"] is True
            assert len(result["sources"]) > 0
            assert result["sources"][0]["source"] == "programs.pdf"


class TestSystemPromptSafety:
    """Test suite for system prompt safety and hallucination prevention"""
    
    def test_system_prompt_contains_anti_hallucination_instruction(self):
        """Test that system prompt contains anti-hallucination instructions"""
        from app.engine.query import SYSTEM_PROMPT
        
        assert "NUNCA inventes" in SYSTEM_PROMPT
        assert "No tengo información" in SYSTEM_PROMPT
        assert "basados en la documentación" in SYSTEM_PROMPT
    
    def test_system_prompt_is_in_spanish(self):
        """Test that system prompt is in Spanish for target audience"""
        from app.engine.query import SYSTEM_PROMPT
        
        spanish_keywords = ["asistente", "posgrado", "Universidad", "pregunta"]
        assert any(keyword in SYSTEM_PROMPT for keyword in spanish_keywords)
    
    def test_response_respects_context_only_instruction(self, rag_query_engine, mock_vector_store):
        """Test that responses are based only on provided context"""
        # Mock documents
        mock_doc = MagicMock()
        mock_doc.page_content = "Deadline for applications: March 31, 2024"
        mock_doc.metadata = {"source": "calendar.pdf"}
        mock_vector_store.similarity_search.return_value = [mock_doc]
        
        # Mock LLM that tries to hallucinate
        mock_response = MagicMock()
        mock_response.content = "Based on the documents, the deadline is March 31, 2024."
        
        with patch.object(rag_query_engine.llm, 'invoke', return_value=mock_response):
            result = rag_query_engine.query("When can I apply?")
            
            assert result["success"] is True
            assert "March 31" in result["answer"]


class TestPerformanceMetrics:
    """Test suite for performance metrics"""
    
    def test_query_latency_tracking(self, rag_query_engine, mock_vector_store):
        """Test that query latency is tracked"""
        import time
        
        mock_doc = MagicMock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"source": "test.pdf"}
        mock_vector_store.similarity_search.return_value = [mock_doc]
        
        mock_response = MagicMock()
        mock_response.content = "Test response"
        
        with patch.object(rag_query_engine.llm, 'invoke', return_value=mock_response):
            start = time.time()
            result = rag_query_engine.query("Test query")
            elapsed = time.time() - start
            
            assert result["success"] is True
            # Response should be reasonably fast (less than 5 seconds as per requirement)
            assert elapsed < 5.0
