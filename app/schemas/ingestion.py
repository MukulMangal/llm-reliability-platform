from datetime import datetime

from pydantic import BaseModel


class IngestionJobResponse(BaseModel):
    id: str
    document_id: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    error: str | None = None