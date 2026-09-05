from fastapi import APIRouter

from app.schemas.search import SearchRequest
from app.services.retrieval_service import retrieval_service

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.post(
    "/",
    summary="Semantic Search",
)
def semantic_search(request: SearchRequest):
    results = retrieval_service.search(
        query=request.query,
        limit=request.limit,
        score_threshold=request.score_threshold,
    )

    return {
        "query": request.query,
        "results": [
            {
                "score": result.score,
                **result.payload,
            }
            for result in results
        ],
    }