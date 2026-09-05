from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
)


class KnowledgeBaseRepository:
    def __init__(self):
        self.knowledge_bases = []
        self.counter = 1

    def create(
        self,
        request: KnowledgeBaseCreate,
    ) -> KnowledgeBaseResponse:

        knowledge_base = KnowledgeBaseResponse(
            id=f"kb_{self.counter:03}",
            name=request.name,
            description=request.description,
            status="created",
        )

        self.knowledge_bases.append(knowledge_base)
        self.counter += 1

        return knowledge_base
    def get_all(self) -> list[KnowledgeBaseResponse]:
        return self.knowledge_bases
    def get_by_id(
    self,
    knowledge_base_id: str,
) -> KnowledgeBaseResponse | None:

     for knowledge_base in self.knowledge_bases:
        if knowledge_base.id == knowledge_base_id:
            return knowledge_base

     return None

    def delete(self, knowledge_base_id: str) -> bool:
        for index, knowledge_base in enumerate(self.knowledge_bases):
            if knowledge_base.id == knowledge_base_id:
                self.knowledge_bases.pop(index)
            return True

        return False


knowledge_base_repository = KnowledgeBaseRepository()