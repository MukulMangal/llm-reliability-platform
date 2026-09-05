from fastapi import APIRouter, HTTPException

from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
)
from app.services.knowledge_base_service import knowledge_base_service

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Bases"],
)


@router.post(
    "/",
    response_model=KnowledgeBaseResponse,
    summary="Create Knowledge Base",
)
def create_knowledge_base(
    request: KnowledgeBaseCreate,
):
    return knowledge_base_service.create(request)


@router.get(
    "/",
    response_model=list[KnowledgeBaseResponse],
    summary="List Knowledge Bases",
)
def list_knowledge_bases():
    return knowledge_base_service.get_all()

@router.get(
    "/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
    summary="Get Knowledge Base",
)

@router.delete(
    "/{knowledge_base_id}",
    summary="Delete Knowledge Base",
)
def delete_knowledge_base(
    knowledge_base_id: str,
):
    deleted = knowledge_base_service.delete(
        knowledge_base_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Knowledge Base not found",
        )

    return {
        "message": "Knowledge Base deleted successfully",
        "id": knowledge_base_id,
    }

def get_knowledge_base(
    knowledge_base_id: str,
):
    knowledge_base = knowledge_base_service.get_by_id(
        knowledge_base_id
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge Base not found",
        )

    return knowledge_base