from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Application!"}

def test_pdf_upload():
    response = client.post("/upload-pdf", files={"file": ("test.pdf", b"PDF content")})
    assert response.status_code == 200
    assert response.json() == {"message": "PDF uploaded successfully."}

def test_query_endpoint():
    response = client.post("/query", json={"query": "What is AI?"})
    assert response.status_code == 200
    assert "results" in response.json()