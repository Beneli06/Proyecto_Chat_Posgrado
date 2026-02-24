"""
Application configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Database Settings
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    
    # LLM Settings
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))
    RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", 5))
    
    # Ingestion Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    
    # API Keys (from environment)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Validation Settings
    MAX_FILE_SIZE = 52428800  # 50MB
    MAX_QUERY_LENGTH = 1000
    RESPONSE_TIMEOUT = 5.0  # seconds


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENVIRONMENT = "development"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENVIRONMENT = "production"


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    ENVIRONMENT = "testing"
    VECTOR_DB_PATH = "./test_chroma_db"


# Select configuration based on environment
config = ProductionConfig() if os.getenv("ENVIRONMENT") == "production" else DevelopmentConfig()
