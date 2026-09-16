"""
ChromaDB Persistent Client and Collection Manager.
"""

import os
from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from src.config.settings import settings
from src.utils.logger import logger


class ChromaManager:
    _instance: Optional["ChromaManager"] = None

    def __init__(self, persist_directory: str = settings.CHROMA_PERSIST_DIRECTORY):
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)

        logger.info(f"Initializing ChromaDB PersistentClient at '{self.persist_directory}'")
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )

        # Initialize collections
        # 1. Sources metadata collection (distance metric cosine)
        self.sources_collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_SOURCES,
            metadata={"description": "Stores indexed URL source documents and metadata"}
        )

        # 2. Document chunks vector collection
        self.chunks_collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_CHUNKS,
            metadata={"hnsw:space": "cosine", "description": "Stores chunk embeddings and context"}
        )

        logger.info("ChromaDB collections ready: sources & chunks.")

    @classmethod
    def get_instance(cls) -> "ChromaManager":
        if cls._instance is None:
            cls._instance = ChromaManager()
        return cls._instance
