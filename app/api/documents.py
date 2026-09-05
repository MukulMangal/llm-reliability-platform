from fastapi import APIRouter, HTTPException

from app.schemas.document import DocumentCreate, DocumentResponse
from app.services.document_service import document_service

router = APIRouter(
    prefix="/knowledge-bases/{knowledge_base_id}",
    tags=["Documents"],
)


@router.post(
    "/text",
    response_model=DocumentResponse,
    summary="Add Raw Text to Knowledge Base",
)
def create_text_document(
    knowledge_base_id: str,
    request: DocumentCreate,
):
    document = document_service.create(
        knowledge_base_id,
        request,
    )

    return document