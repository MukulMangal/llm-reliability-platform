from app.repositories.vector_repository import vector_repository
from app.services.embedding_service import embedding_service


class RetrievalService:

    def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.5,
    ):
        query_embedding = embedding_service.embed_text(query)

        candidate_limit = max(
            limit * 3,
            limit,
        )

        results = vector_repository.search(
            query_embedding,
            limit=candidate_limit,
            score_threshold=score_threshold,
        )

        unique_results = []
        seen_content = set()

        for result in results:
            content = result.payload.get(
                "content",
                "",
            ).strip()

            if content in seen_content:
                continue

            seen_content.add(content)
            unique_results.append(result)

            if len(unique_results) >= limit:
                break

        return unique_results


retrieval_service = RetrievalService()