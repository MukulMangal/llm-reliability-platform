from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.agent_service import agent_service


router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"],
)


class AgentRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural-language request for the Razorpay operations agent.",
        examples=[
            "Create a payment link for ₹500 for a test order",
            "Check payment pay_test123",
            "Refund payment pay_test123",
        ],
    )


class AgentResponse(BaseModel):
    success: bool = Field(
        description="Whether the requested operation completed successfully."
    )
    operation: str = Field(
        description="Razorpay operation selected by the agent."
    )
    status: str = Field(
        description="Execution status of the operation."
    )
    message: str | None = Field(
        default=None,
        description="Human-readable message when an operation fails or is rejected.",
    )
    result: dict | None = Field(
        default=None,
        description="Verified result returned by the Razorpay API.",
    )
    reliability: dict | None = Field(
        default=None,
        description="Reliability assessment of the verified Razorpay result.",
    )


@router.post(
    "/",
    summary="Run Razorpay AI Agent",
    description=(
        "Interpret a natural-language Razorpay request, validate it "
        "using deterministic guardrails, execute an allowed operation, "
        "and return a reliability assessment."
    ),
    response_model=AgentResponse,
    responses={
        200: {
            "description": "Agent processed the request.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "operation": "create_payment_link",
                        "status": "completed",
                        "message": None,
                        "result": {
                            "id": "plink_test123",
                            "amount": 50000,
                            "currency": "INR",
                            "status": "created",
                            "short_url": "https://rzp.io/rzp/example",
                        },
                        "reliability": {
                            "reliability_score": 1.0,
                            "reliability_status": "highly_supported",
                            "confidence_level": "high",
                        },
                    }
                }
            },
        },
    },
)
def run_agent(request: AgentRequest):
    return agent_service.execute(request.query)