from fastapi import APIRouter

from app.schemas.query import QueryRequest, QueryResponse

from app.services.rag_service import rag_service


router = APIRouter(
    prefix="/query",
    tags=["RAG"],
)


@router.post(
    "/",
    summary="Ask a Question",
    description=(
        "Answer a question using evidence retrieved from the knowledge base. "
        "The response includes the generated answer, retrieved sources, "
        "claim-level verification, reliability status, and confidence level."
    ),
    response_model=QueryResponse,
)
def ask_question(request: QueryRequest):

    return rag_service.answer(
        query=request.query,
        limit=request.limit,
        score_threshold=request.score_threshold,
    )