from dataclasses import dataclass
from datetime import datetime


@dataclass
class IngestionJob:
    id: str
    document_id: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    error: str | None = None