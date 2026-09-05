from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


class VectorRepository:
    COLLECTION_NAME = "document_chunks"
    VECTOR_SIZE = 384

    def __init__(self):
        data_path = Path("data/qdrant")

        self.client = QdrantClient(
            path=str(data_path),
        )

        if not self.client.collection_exists(self.COLLECTION_NAME):
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    def add_vector(
        self,
        vector_id: int,
        embedding: list[float],
        payload: dict,
    ) -> None:
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                PointStruct(
                    id=vector_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )

    def search(
        self,
        embedding: list[float],
        limit: int = 5,
        score_threshold: float = 0.5,
    ):
        return self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=embedding,
            limit=limit,
            score_threshold=score_threshold,
        ).points


vector_repository = VectorRepository()