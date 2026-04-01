import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM - OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Gemini (keeping for future use)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./healthcare_auth.db"
    )
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        "./chroma_db"
    )
    CHROMA_COLLECTION_POLICY: str = "insurance_policies"
    CHROMA_COLLECTION_CLINICAL: str = "clinical_notes"
    
    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5

config = Config()