from enum import Enum

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):

    query: str = Field(
        min_length=1,
        description="Question to answer using the knowledge base.",
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of unique evidence chunks to retrieve.",
    )

    score_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score required for retrieved evidence.",
    )


class ReliabilityStatus(str, Enum):

    HIGHLY_SUPPORTED = "highly_supported"

    PARTIALLY_SUPPORTED = "partially_supported"

    UNSUPPORTED = "unsupported"

    SAFE_REFUSAL = "safe_refusal"


class ConfidenceLevel(str, Enum):

    HIGH = "high"

    MEDIUM = "medium"

    LOW = "low"


class QuerySource(BaseModel):

    score: float = Field(
        description="Similarity score of the retrieved evidence chunk.",
    )

    chunk_id: str = Field(
        description="Unique identifier of the retrieved chunk.",
    )

    document_id: str = Field(
        description="Identifier of the source document.",
    )

    content: str = Field(
        description="Text content used as evidence.",
    )


class QueryClaim(BaseModel):

    text: str = Field(
        description="Claim extracted from the generated answer.",
    )

    supported: bool = Field(
        description="Whether the claim is supported by the retrieved evidence.",
    )

    evidence: str = Field(
        description="Evidence used to verify the claim.",
    )


class QueryResponse(BaseModel):

    query: str = Field(
        description="Original user question.",
    )

    answer: str = Field(
        description="Answer generated from the retrieved knowledge-base evidence.",
    )

    reliability_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall reliability score combining claim support and retrieval quality.",
    )

    claim_support_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Proportion of generated claims supported by the evidence.",
    )

    retrieval_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Highest similarity score among the retrieved evidence chunks.",
    )

    reliability_status: ReliabilityStatus = Field(
        description="Overall evidence-support status of the generated answer.",
    )

    confidence_level: ConfidenceLevel = Field(
        description="Confidence level derived from reliability evaluation.",
    )

    claims: list[QueryClaim] = Field(
        description="Claims extracted from the generated answer and their verification results.",
    )

    supported_claims: int = Field(
        ge=0,
        description="Number of generated claims supported by the evidence.",
    )

    total_claims: int = Field(
        ge=0,
        description="Total number of claims extracted from the generated answer.",
    )

    sources: list[QuerySource] = Field(
        description="Evidence chunks retrieved from the knowledge base.",
    )