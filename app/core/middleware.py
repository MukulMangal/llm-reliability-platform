import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI) -> None:
    """
    Register application middleware.
    """

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            "%s %s completed in %.4f seconds",
            request.method,
            request.url.path,
            process_time,
        )

        return response