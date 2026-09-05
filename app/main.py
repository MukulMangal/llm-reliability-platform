from fastapi import FastAPI

from app.api.system import router as system_router
from app.api.knowledge_bases import router as knowledge_base_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.core.middleware import register_middleware
from app.api.documents import router as document_router
from app.api.search import router as search_router
from app.api.query import router as query_router
from app.api.knowledge_graph import router as knowledge_graph_router
from app.api.agent import router as agent_router

setup_logging()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)
register_exception_handlers(app)
register_middleware(app)

app.include_router(system_router)
app.include_router(knowledge_base_router)
app.include_router(document_router)
app.include_router(search_router)
app.include_router(query_router)
app.include_router(knowledge_graph_router)
app.include_router(agent_router)