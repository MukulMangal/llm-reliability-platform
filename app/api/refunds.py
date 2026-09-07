from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.agent_tools import agent_tools
from app.services.razorpay_service import razorpay_service


router = APIRouter(
    prefix="/refunds",
    tags=["Refunds"],
)


class CreateRefundRequest(BaseModel):
    payment_id: str = Field(
        min_length=1,
        description="Razorpay payment ID to refund.",
        examples=["pay_test123"],
    )
    amount: int | None = Field(
        default=None,
        gt=0,
        description=(
            "Optional refund amount in paise. "
            "Omit for a full refund."
        ),
        examples=[50000],
    )


@router.get(
    "/",
    summary="Get Refunds",
    description=(
        "Retrieve recent refunds from Razorpay Test Mode."
    ),
)
def get_refunds(
    count: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of refunds to retrieve.",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of refunds to skip.",
    ),
):
    response = razorpay_service.list_refunds(
        count=count,
        skip=skip,
    )

    refunds = response.get(
        "items",
        [],
    )

    return {
        "refunds": refunds,
        "count": len(refunds),
    }


@router.post(
    "/",
    summary="Create Refund",
    description=(
        "Create a full or partial refund after deterministic "
        "validation of the payment state and refund amount."
    ),
)
def create_refund(
    request: CreateRefundRequest,
):
    refund = agent_tools.refund_payment(
        payment_id=request.payment_id.strip(),
        amount=request.amount,
    )

    return {
        "refund": refund,
    }