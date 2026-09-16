"""
ChromaDB Knowledge Base Erasure & Reset Script.

Run this script to erase all ingested sources and vector chunk embeddings
from ChromaDB persistent storage.

Usage:
    python clear_chromadb.py
"""

import sys
import os

# Add Backend root directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.rag.components.vector_store.repository import VectorRepository
from src.utils.logger import logger

def main():
    print("=" * 60)
    print(" 🗑️  ChromaDB Data Erasure Script")
    print("=" * 60)

    repo = VectorRepository()
    stats_before = repo.get_statistics()
    print(f"Current Status BEFORE reset:")
    print(f" - Total Sources: {stats_before['total_sources']}")
    print(f" - Total Chunks:  {stats_before['total_chunks']}")
    print(f" - Total Chars:   {stats_before['total_characters']}")

    if stats_before['total_sources'] == 0 and stats_before['total_chunks'] == 0:
        print("\n✨ ChromaDB is already empty. Nothing to erase.")
        return

    confirm = input("\n⚠️  Are you sure you want to PERMANENTLY delete all ingested data? (y/N): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Operation cancelled. No data was deleted.")
        return

    print("\nErasing all ChromaDB vector storage & source metadata...")
    metrics = repo.clear_all()
    
    stats_after = repo.get_statistics()
    print("\n✅ Reset completed successfully!")
    print(f" - Sources Erased: {metrics.get('deleted_sources', 0)}")
    print(f" - Chunks Erased:  {metrics.get('deleted_chunks', 0)}")
    print(f" - Remaining Sources: {stats_after['total_sources']}")
    print(f" - Remaining Chunks:  {stats_after['total_chunks']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
