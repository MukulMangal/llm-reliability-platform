from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    id: str
    knowledge_base_id: str
    title: str
    source_type: str
    content: str
    status: str
    created_at: datetime