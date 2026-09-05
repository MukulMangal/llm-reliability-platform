from datetime import datetime

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    content: str = Field(
        min_length=1,
    )


class DocumentResponse(BaseModel):

    id: str

    knowledge_base_id: str

    title: str

    source_type: str

    content: str

    status: str

    created_at: datetime