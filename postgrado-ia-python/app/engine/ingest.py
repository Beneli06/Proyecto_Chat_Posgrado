"""
PDF Ingestion Engine - Handles PDF parsing, chunking, and embedding generation
"""

import os
from typing import List, Optional
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import logging

logger = logging.getLogger(__name__)


class PDFIngestionEngine:
    """
    Handles ingestion of PDF documents into the RAG system.
    
    Process:
    1. Load PDF files
    2. Split into chunks with overlap
    3. Generate embeddings
    4. Store in vector database
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "text-embedding-3-small",
        vector_db_path: str = "./chroma_db"
    ):
        """
        Initialize the PDF ingestion engine.
        
        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks for context preservation
            embedding_model: OpenAI embedding model to use
            vector_db_path: Path to store the vector database
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
        self.vector_db_path = vector_db_path
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize vector store
        self.vector_store = None
        self._init_vector_store()
    
    def _init_vector_store(self):
        """Initialize or load existing vector store."""
        try:
            self.vector_store = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            logger.info(f"Loaded existing vector store from {self.vector_db_path}")
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {e}")
            self.vector_store = None
    
    def ingest_pdf(
        self,
        pdf_path: str,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Ingest a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            metadata: Optional metadata (e.g., program name, update date)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate PDF file
        if not pdf_path.lower().endswith('.pdf'):
            logger.error(f"Invalid file type. Expected PDF, got {pdf_path}")
            return False
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        
        try:
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {pdf_path}")
            
            # Add metadata to documents
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")
            
            # Store in vector database
            if self.vector_store is None:
                self.vector_store = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=self.vector_db_path
                )
            else:
                self.vector_store.add_documents(chunks)
            
            self.vector_store.persist()
            logger.info(f"Successfully ingested {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting PDF {pdf_path}: {str(e)}")
            return False
    
    def ingest_multiple_pdfs(self, pdf_dir: str) -> dict:
        """
        Ingest all PDFs from a directory.
        
        Args:
            pdf_dir: Directory containing PDF files
            
        Returns:
            dict: Statistics of ingestion process
        """
        stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        if not os.path.isdir(pdf_dir):
            stats["errors"].append(f"Directory not found: {pdf_dir}")
            return stats
        
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        stats["total"] = len(pdf_files)
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_dir, pdf_file)
            metadata = {
                "source_file": pdf_file,
                "file_type": "pdf"
            }
            
            if self.ingest_pdf(pdf_path, metadata):
                stats["successful"] += 1
            else:
                stats["failed"] += 1
                stats["errors"].append(f"Failed to ingest {pdf_file}")
        
        return stats
