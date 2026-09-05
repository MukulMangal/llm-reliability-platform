from pydantic import BaseModel, Field


class Entity(BaseModel):
    name: str
    entity_type: str = "unknown"


class Relationship(BaseModel):
    source: str
    relation: str
    target: str


class KnowledgeGraph(BaseModel):
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)