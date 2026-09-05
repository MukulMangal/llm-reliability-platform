from app.services.knowledge_graph_service import knowledge_graph_service
from app.services.llm_service import llm_service
from app.services.retrieval_service import retrieval_service
from app.services.reliability_service import reliability_service


class RAGService:
    def answer(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.5,
    ) -> dict:

        results = retrieval_service.search(
            query=query,
            limit=limit,
            score_threshold=score_threshold,
        )

        if not results:
            return {
                "query": query,
                "answer": "I could not find relevant information in the knowledge base.",
                "reliability_score": 0.0,
                "claim_support_score": 0.0,
                "retrieval_score": 0.0,
                "claims": [],
                "supported_claims": 0,
                "total_claims": 0,
                "sources": [],
                "reliability_status": "safe_refusal",
                "confidence_level": "low",
            }

        vector_context = "\n\n".join(
            f"[Source {index + 1}]\n{result.payload['content']}"
            for index, result in enumerate(results)
        )

        graph_context = knowledge_graph_service.get_context(query)

        combined_context = vector_context

        if graph_context:
            combined_context += (
                "\n\n[Knowledge Graph Context]\n"
                + graph_context
            )

        prompt = f"""
You are a reliable question-answering assistant.

Answer the user's question using ONLY the provided context.

The context contains:
1. Text evidence retrieved from documents.
2. Structured relationships from the Knowledge Graph.

Rules:
- Do not use outside knowledge.
- Do not invent facts.
- Prefer information supported by the provided text.
- Knowledge Graph relationships may help clarify relationships between entities.
- If the context does not contain enough information, say so.

Context:
{combined_context}

Question:
{query}

Answer:
""".strip()

        answer = llm_service.generate(prompt)

        refusal_phrases = [
            "i could not find relevant information",
            "there is no information",
            "there is insufficient information",
            "the information is insufficient",
            "i don't have enough information",
            "the context does not contain enough information",
        ]

        is_refusal = any(
            phrase in answer.lower()
            for phrase in refusal_phrases
        )

        retrieval_score = max(
            result.score
            for result in results
        )

        if is_refusal:
            reliability = {
                "reliability_score": 0.0,
                "claim_support_score": 0.0,
                "retrieval_score": retrieval_score,
                "claims": [],
                "supported_claims": 0,
                "total_claims": 0,
                "reliability_status": "safe_refusal",
            }
        else:
            reliability = reliability_service.analyze(
                answer=answer,
                evidence=combined_context,
                retrieval_score=retrieval_score,
            )

        return {
            "query": query,
            "answer": answer,
            "reliability_score": reliability["reliability_score"],
            "claim_support_score": reliability["claim_support_score"],
            "retrieval_score": reliability["retrieval_score"],
            "reliability_status": reliability.get(
                "reliability_status",
                "evaluated",
            ),
            "confidence_level": reliability.get(
                "confidence_level",
                "low",
            ),
            "claims": reliability["claims"],
            "supported_claims": reliability["supported_claims"],
            "total_claims": reliability["total_claims"],
            "sources": [
                {
                    "score": result.score,
                    "chunk_id": result.payload["chunk_id"],
                    "document_id": result.payload["document_id"],
                    "content": result.payload["content"],
                }
                for result in results
            ],
        }


rag_service = RAGService()