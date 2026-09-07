from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.razorpay_service import razorpay_service


router = APIRouter(
    prefix="/payment-links",
    tags=["Payment Links"],
)


class CreatePaymentLinkRequest(BaseModel):
    amount: int = Field(
        gt=0,
        description="Payment amount in paise.",
        examples=[50000],
    )
    description: str = Field(
        min_length=1,
        description="Description shown for the payment link.",
        examples=["Test order"],
    )
    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
        description="Three-letter currency code.",
        examples=["INR"],
    )


@router.get(
    "/",
    summary="Get Payment Links",
    description=(
        "Retrieve recent Payment Links from Razorpay Test Mode."
    ),
)
def get_payment_links(
    count: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of payment links to retrieve.",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of payment links to skip.",
    ),
):
    response = razorpay_service.list_payment_links(
        count=count,
        skip=skip,
    )

    payment_links = response.get(
        "payment_links",
        [],
    )

    return {
        "payment_links": payment_links,
        "count": len(payment_links),
    }


@router.post(
    "/",
    summary="Create Payment Link",
    description=(
        "Create a Razorpay Payment Link in Test Mode."
    ),
)
def create_payment_link(
    request: CreatePaymentLinkRequest,
):
    payment_link = razorpay_service.create_payment_link(
        amount=request.amount,
        description=request.description.strip(),
        currency=request.currency.upper(),
    )

    return {
        "payment_link": payment_link,
    }