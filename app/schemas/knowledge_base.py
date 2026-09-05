from pydantic import BaseModel


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: str


class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str