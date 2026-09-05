from app.models.chunk import Chunk


class ChunkRepository:
    def __init__(self):
        self.chunks = []
        self.counter = 1

    def create_many(self, chunks: list[Chunk]) -> list[Chunk]:
        self.chunks.extend(chunks)
        self.counter += len(chunks)
        return chunks

    def get_by_document(
        self,
        document_id: str,
    ) -> list[Chunk]:
        return [
            chunk
            for chunk in self.chunks
            if chunk.document_id == document_id
        ]


chunk_repository = ChunkRepository()