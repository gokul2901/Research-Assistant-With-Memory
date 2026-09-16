"""
Root entry point for Research Assistant with Persistent Memory.
"""

import sys
import os

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from src.main import app, settings
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
