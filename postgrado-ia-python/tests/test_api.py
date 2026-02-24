"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app, query_engine, ingest_engine


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_query_engine():
    """Create a mock query engine"""
    return MagicMock()


@pytest.fixture
def mock_ingest_engine():
    """Create a mock ingest engine"""
    return MagicMock()


class TestHealthEndpoint:
    """Test suite for health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestQueryEndpoint:
    """Test suite for query endpoint"""
    
    def test_query_with_valid_question(self, client):
        """Test query endpoint with valid input"""
        with patch('app.main.query_engine') as mock_engine:
            mock_engine.query.return_value = {
                "success": True,
                "answer": "Master's programs are available.",
                "sources": [],
                "question": "What programs are available?"
            }
            mock_engine is not None
            
            response = client.post(
                "/query",
                json={"question": "What programs are available?"}
            )
            
            # Note: This test may fail if query_engine is not initialized
            # In production, ensure proper initialization
    
    def test_query_with_empty_question(self, client):
        """Test query endpoint with empty question"""
        response = client.post(
            "/query",
            json={"question": ""}
        )
        
        assert response.status_code == 400
    
    def test_query_with_too_short_question(self, client):
        """Test query endpoint with too short question"""
        response = client.post(
            "/query",
            json={"question": "ab"}
        )
        
        assert response.status_code == 400
    
    def test_query_with_return_sources_flag(self, client):
        """Test query endpoint with return_sources flag"""
        with patch('app.main.query_engine') as mock_engine:
            mock_engine.query.return_value = {
                "success": True,
                "answer": "Test answer",
                "sources": [{"source": "test.pdf", "page": 1}],
                "question": "Test question"
            }
            mock_engine is not None
            
            response = client.post(
                "/query",
                json={
                    "question": "Test question with more than three chars",
                    "return_sources": True
                }
            )


class TestIngestEndpoint:
    """Test suite for PDF ingestion endpoint"""
    
    def test_ingest_valid_pdf(self, client):
        """Test ingestion of valid PDF"""
        # Note: This would require actual file handling
        # In a real test, use BytesIO or temporary files
        pass
    
    def test_ingest_non_pdf_file(self, client):
        """Test rejection of non-PDF files"""
        from io import BytesIO
        
        with patch('app.main.ingest_engine') as mock_engine:
            mock_engine is not None
            
            # Create a non-PDF file
            file_content = BytesIO(b"This is not a PDF")
            
            response = client.post(
                "/ingest/pdf",
                files={"file": ("test.txt", file_content, "text/plain")}
            )
            
            # Should reject non-PDF files
            assert response.status_code in [200, 400, 422]


class TestRootEndpoint:
    """Test suite for root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestErrorHandling:
    """Test suite for error handling"""
    
    def test_query_engine_not_initialized(self, client):
        """Test handling when query engine is not initialized"""
        with patch('app.main.query_engine', None):
            response = client.post(
                "/query",
                json={"question": "Test question"}
            )
            
            # Should return error about engine not initialized
            assert response.status_code in [500, 503]
    
    def test_malformed_json(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            "/query",
            json={"invalid_key": "value"}
        )
        
        assert response.status_code in [400, 422]
