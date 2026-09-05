from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
)
from app.repositories.knowledge_base_repository import (
    knowledge_base_repository,
)


class KnowledgeBaseService:
   def create(
    self,
    request: KnowledgeBaseCreate,
) -> KnowledgeBaseResponse:

    return knowledge_base_repository.create(request)
   def get_all(self) -> list[KnowledgeBaseResponse]:
    return knowledge_base_repository.get_all()
   def get_by_id(
    self,
    knowledge_base_id: str,
) -> KnowledgeBaseResponse | None:

    return knowledge_base_repository.get_by_id(
        knowledge_base_id
    )
   def delete(self, knowledge_base_id: str) -> bool:
    return knowledge_base_repository.delete(knowledge_base_id)


knowledge_base_service = KnowledgeBaseService()