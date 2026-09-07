from fastapi import APIRouter, Query

from app.services.activity_service import activity_service


router = APIRouter(
    prefix="/activity",
    tags=["Activity"],
)


@router.get(
    "/",
    summary="Get Agent Activity",
    description=(
        "Return recent AI payment-operation activity, including "
        "execution status and reliability information."
    ),
)
def get_activity(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of recent activity records to return.",
    ),
):
    activities = activity_service.list_recent(limit)

    return {
        "activities": activities,
        "count": len(activities),
    }