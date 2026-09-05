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
    )


class AgentResponse(BaseModel):
    success: bool
    operation: str
    status: str
    message: str | None = None
    result: dict | None = None
    reliability: dict | None = None


@router.post(
    "/",
    summary="Run Razorpay AI Agent",
    description=(
        "Interpret a natural-language Razorpay request, validate it "
        "using deterministic guardrails, execute an allowed operation, "
        "and return a reliability assessment."
    ),
    response_model=AgentResponse,
)
def run_agent(request: AgentRequest):
    return agent_service.execute(request.query)