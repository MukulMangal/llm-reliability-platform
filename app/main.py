from fastapi import FastAPI

from app.api.system import router as system_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.core.middleware import register_middleware

setup_logging()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)
register_exception_handlers(app)
register_middleware(app)

app.include_router(system_router)