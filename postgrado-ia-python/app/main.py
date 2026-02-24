"""
FastAPI application for the RAG Chatbot
"""

import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
from typing import Optional, List
import time

from app.engine import PDFIngestionEngine, RAGQueryEngine
from app.utils import get_logger, validate_pdf_file, validate_query

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot for University Postgraduate Programs",
    description="AI-powered chatbot for answering postgraduate program inquiries",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
ingest_engine = None
query_engine = None


# Pydantic models
class QueryRequest(BaseModel):
    """Query request model"""
    question: str = Field(..., description="The user's question")
    return_sources: bool = Field(default=True, description="Whether to return source documents")


class QueryResponse(BaseModel):
    """Query response model"""
    success: bool
    answer: Optional[str]
    sources: List[dict] = Field(default_factory=list)
    question: Optional[str] = None
    error: Optional[str] = None


class IngestionResponse(BaseModel):
    """PDF ingestion response model"""
    success: bool
    message: str
    file_name: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vector_db_connected: bool
    llm_available: bool


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize engines on startup"""
    global ingest_engine, query_engine
    
    logger.info("Starting RAG Chatbot application...")
    
    try:
        vector_db_path = os.getenv("VECTOR_DB_PATH", "./chroma_db")
        
        ingest_engine = PDFIngestionEngine(
            chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 200)),
            vector_db_path=vector_db_path
        )
        logger.info("PDF Ingestion Engine initialized")
        
        query_engine = RAGQueryEngine(
            vector_db_path=vector_db_path,
            model_name=os.getenv("LLM_MODEL", "gpt-4"),
            temperature=float(os.getenv("TEMPERATURE", 0.3)),
            max_tokens=int(os.getenv("MAX_TOKENS", 1000)),
            retrieval_k=int(os.getenv("RETRIEVAL_K", 5))
        )
        logger.info("RAG Query Engine initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize engines: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down RAG Chatbot application...")


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        vector_db_connected=query_engine is not None and query_engine.vector_store is not None,
        llm_available=query_engine is not None
    )


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Query the RAG system.
    
    Args:
        request: QueryRequest containing the question
        
    Returns:
        QueryResponse: The answer and sources
    """
    # Validate query
    is_valid, error = validate_query(request.question)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Check if query engine is initialized
    if query_engine is None:
        raise HTTPException(
            status_code=503,
            detail="RAG Query Engine not initialized"
        )
    
    # Measure response time
    start_time = time.time()
    
    try:
        # Process query
        result = query_engine.query(
            question=request.question,
            return_sources=request.return_sources
        )
        
        elapsed_time = time.time() - start_time
        
        # Check latency requirement (5 seconds max)
        if elapsed_time > 5.0:
            logger.warning(f"Query latency exceeded 5s: {elapsed_time:.2f}s")
        
        logger.info(f"Query processed in {elapsed_time:.2f}s")
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error processing query"
        )


@app.post("/ingest/pdf", response_model=IngestionResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Ingest a PDF document.
    
    Args:
        file: The PDF file to ingest
        
    Returns:
        IngestionResponse: Status of ingestion
    """
    # Check if ingest engine is initialized
    if ingest_engine is None:
        raise HTTPException(
            status_code=503,
            detail="PDF Ingestion Engine not initialized"
        )
    
    try:
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            return IngestionResponse(
                success=False,
                message="Invalid file type",
                error="Only PDF files are accepted"
            )
        
        # Save temporary file
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate PDF
        is_valid, error = validate_pdf_file(temp_path)
        if not is_valid:
            return IngestionResponse(
                success=False,
                message="PDF validation failed",
                error=error
            )
        
        # Ingest PDF
        metadata = {
            "program": file.filename.split('.')[0],
            "uploaded_at": str(time.time())
        }
        
        success = ingest_engine.ingest_pdf(temp_path, metadata)
        
        # Cleanup
        os.remove(temp_path)
        
        if success:
            return IngestionResponse(
                success=True,
                message=f"PDF '{file.filename}' successfully ingested",
                file_name=file.filename
            )
        else:
            return IngestionResponse(
                success=False,
                message="Failed to ingest PDF",
                error="An error occurred during ingestion"
            )
        
    except Exception as e:
        logger.error(f"Error ingesting PDF: {str(e)}")
        return IngestionResponse(
            success=False,
            message="Error ingesting PDF",
            error=str(e)
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Chatbot API",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "production") == "development"
    )
