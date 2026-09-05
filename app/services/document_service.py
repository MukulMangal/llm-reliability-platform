from datetime import datetime, timezone

from app.models.document import Document
from app.repositories.document_repository import document_repository
from app.schemas.document import DocumentCreate
from app.services.chunk_service import chunk_service
from app.services.knowledge_graph_service import knowledge_graph_service


class DocumentService:
    def create(
        self,
        knowledge_base_id: str,
        request: DocumentCreate,
    ) -> Document:

        document = Document(
            id=f"doc_{document_repository.counter:03}",
            knowledge_base_id=knowledge_base_id,
            title=request.title,
            source_type="text",
            content=request.content,
            status="created",
            created_at=datetime.now(timezone.utc),
        )

        created_document = document_repository.create(document)
        chunk_service.create_from_document(
            document_id=created_document.id,
            content=created_document.content,
        )
        knowledge_graph_service.extract_and_store(
            created_document.content
)
        return created_document

    def get_by_id(
        self,
        document_id: str,
    ) -> Document | None:

        return document_repository.get_by_id(document_id)

    def get_by_knowledge_base(
        self,
        knowledge_base_id: str,
    ) -> list[Document]:

        return document_repository.get_by_knowledge_base(
            knowledge_base_id
        )


document_service = DocumentService()