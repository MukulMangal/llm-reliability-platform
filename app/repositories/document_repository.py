from app.models.document import Document


class DocumentRepository:
    def __init__(self):
        self.documents = []
        self.counter = 1

    def create(self, document: Document) -> Document:
        self.documents.append(document)
        self.counter += 1
        return document

    def get_by_id(self, document_id: str) -> Document | None:
        for document in self.documents:
            if document.id == document_id:
                return document

        return None

    def get_by_knowledge_base(
        self,
        knowledge_base_id: str,
    ) -> list[Document]:
        return [
            document
            for document in self.documents
            if document.knowledge_base_id == knowledge_base_id
        ]


document_repository = DocumentRepository()