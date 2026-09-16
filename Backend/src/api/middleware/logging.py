"""
FastAPI Request Logging and Timing Middleware.
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from src.utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start_time = time.perf_counter()

        logger.info(f"[{request_id}] {request.method} {request.url.path} - Started")

        try:
            response = await call_next(request)
            process_time = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Process-Time"] = f"{process_time}ms"
            response.headers["X-Request-ID"] = request_id

            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Status: {response.status_code} in {process_time}ms"
            )
            return response
        except Exception as e:
            process_time = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Unhandled Exception: {str(e)} in {process_time}ms"
            )
            raise e
