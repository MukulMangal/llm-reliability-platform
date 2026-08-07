from fastapi import APIRouter
from app.core.config import settings
import logging


logger = logging.getLogger(__name__)

router = APIRouter(tags=["System"])


@router.get(
    "/",
    summary="Welcome",
    description="Root endpoint of the LLM Reliability Platform."
)
def root():
    return {
        "message": "Welcome to the LLM Reliability Platform!"
    }


@router.get(
    "/health",
    summary="Health Check",
    description="Returns the current health status of the application."
)
def health():
    logger.info("Health endpoint accessed")
    return {
    "status": "healthy",
    "application": settings.PROJECT_NAME,
    "version": settings.VERSION,
    "environment": "development",
    }


@router.get(
    "/info",
    summary="Application Information",
    description="Returns metadata about the application."
)
def info():
    return {
    "project": settings.PROJECT_NAME,
    "version": settings.VERSION,
    }
