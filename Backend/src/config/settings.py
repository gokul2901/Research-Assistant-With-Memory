"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application Settings
    APP_NAME: str = "Research Assistant with Persistent Memory"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "production-secret-key-change-in-prod"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Vector Database (ChromaDB)
    CHROMA_PERSIST_DIRECTORY: str = "./data/chromadb"
    CHROMA_COLLECTION_SOURCES: str = "research_sources"
    CHROMA_COLLECTION_CHUNKS: str = "research_chunks"

    # Embedding Configuration
    EMBEDDING_PROVIDER: str = "fastembed"  # "fastembed", "openai", or "litellm"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_BATCH_SIZE: int = 32

    # LiteLLM Multi-Model Router (Primary + Fallbacks)
    PRIMARY_MODEL: str = "gemini/gemini-2.5-flash"
    FALLBACK_MODEL_1: str = "zhipu/glm-4"
    FALLBACK_MODEL_2: str = "groq/llama-3.3-70b-versatile"

    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    MIST_API_KEY: Optional[str] = None
    ZHIPUAI_API_KEY: Optional[str] = None
    GLM_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Chunking Configuration
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    # Retrieval Configuration
    DEFAULT_TOP_K: int = 5
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.15
    MAX_TOP_K: int = 20

    # n8n Automation & Webhook Integration
    N8N_WEBHOOK_URL: Optional[str] = None
    N8N_CALLBACK_SECRET: str = "production-n8n-secret-change-in-prod"

    # Web Scraping & Ingestion
    SCRAPER_USER_AGENT: str = "ResearchAssistantBot/1.0"
    USER_AGENT: str = "ResearchAssistantBot/1.0"
    SCRAPE_TIMEOUT_SECONDS: int = 20
    SCRAPER_TIMEOUT_SECONDS: int = 20
    SCRAPER_MAX_RETRIES: int = 3
    MAX_RESPONSE_SIZE_MB: int = 10
    MAX_CONTENT_LENGTH: int = 1000000
    MAX_REDIRECTS: int = 5
    MAX_RETRIES: int = 3
    MIN_CONTENT_LENGTH: int = 50
    MAX_CONCURRENT_SCRAPES: int = 5
    ENABLE_SSRF_PROTECTION: bool = True

    # PDF Export Settings
    PDF_EXPORT_DIR: str = "./data/exports"


settings = Settings()
