from fastapi import APIRouter, Query

from app.services.razorpay_service import razorpay_service


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.get(
    "/",
    summary="Get Payments",
    description=(
        "Retrieve recent payments from Razorpay Test Mode."
    ),
)
def get_payments(
    count: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of payments to retrieve.",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of payments to skip.",
    ),
):
    response = razorpay_service.list_payments(
        count=count,
        skip=skip,
    )

    payments = response.get("items", [])

    return {
        "payments": payments,
        "count": len(payments),
    }