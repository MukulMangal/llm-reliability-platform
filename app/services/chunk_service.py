from app.models.chunk import Chunk
from app.repositories.chunk_repository import chunk_repository
from app.repositories.vector_repository import vector_repository
from app.services.chunking_service import chunking_service
from app.services.embedding_service import embedding_service


class ChunkService:
    def create_from_document(
        self,
        document_id: str,
        content: str,
    ) -> list[Chunk]:

        text_chunks = chunking_service.chunk_text(content)

        chunks = [
            Chunk(
                id=f"chunk_{chunk_repository.counter + index:03}",
                document_id=document_id,
                content=text,
                chunk_index=index,
            )
            for index, text in enumerate(text_chunks)
        ]

        stored_chunks = chunk_repository.create_many(chunks)

        embeddings = embedding_service.embed_many(
            [chunk.content for chunk in stored_chunks]
        )

        for index, (chunk, embedding) in enumerate(
            zip(stored_chunks, embeddings)
        ):
            vector_repository.add_vector(
                vector_id=chunk_repository.counter - len(stored_chunks) + index,
                embedding=embedding,
                payload={
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "chunk_index": chunk.chunk_index,
                },
            )

        return stored_chunks

    def get_by_document(
        self,
        document_id: str,
    ) -> list[Chunk]:

        return chunk_repository.get_by_document(document_id)


chunk_service = ChunkService()