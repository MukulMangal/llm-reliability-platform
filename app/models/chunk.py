from dataclasses import dataclass


@dataclass
class Chunk:
    id: str
    document_id: str
    content: str
    chunk_index: int