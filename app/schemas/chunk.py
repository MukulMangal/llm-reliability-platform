from pydantic import BaseModel


class ChunkResponse(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int