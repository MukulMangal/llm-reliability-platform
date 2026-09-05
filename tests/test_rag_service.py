from app.services.rag_service import RAGService


def test_rag_returns_reliability_results(monkeypatch):
    service = RAGService()

    monkeypatch.setattr(
        "app.services.rag_service.retrieval_service.search",
        lambda query, limit, score_threshold: [
            type(
                "Result",
                (),
                {
                    "score": 0.8,
                    "payload": {
                        "content": (
                            "Diabetes may increase the risk "
                            "of cardiovascular disease."
                        ),
                        "title": "Diabetes Guide",
                        "document_id": "doc-1",
                        "chunk_id": "chunk-1",
                    },
                },
            )()
        ],
    )

    monkeypatch.setattr(
        "app.services.rag_service.llm_service.generate",
        lambda prompt: (
            "Diabetes may increase the risk of "
            "cardiovascular disease."
        ),
    )

    expected_reliability = {
        "reliability_score": 0.94,
        "claim_support_score": 1.0,
        "retrieval_score": 0.8,
        "reliability_status": "highly_supported",
        "confidence_level": "high",
        "claims": [
            {
                "text": (
                    "Diabetes may increase the risk "
                    "of cardiovascular disease."
                ),
                "supported": True,
                "evidence": (
                    "Diabetes may increase the risk "
                    "of cardiovascular disease."
                ),
            }
        ],
        "supported_claims": 1,
        "total_claims": 1,
    }

    monkeypatch.setattr(
        "app.services.rag_service.reliability_service.analyze",
        lambda answer, evidence, retrieval_score:
            expected_reliability,
    )

    result = service.answer(
        query="What health risk is associated with diabetes?",
        limit=5,
        score_threshold=0.5,
    )

    assert result["answer"] == (
        "Diabetes may increase the risk of "
        "cardiovascular disease."
    )

    assert result["reliability_score"] == 0.94
    assert result["claim_support_score"] == 1.0
    assert result["retrieval_score"] == 0.8
    assert result["reliability_status"] == "highly_supported"
    assert result["confidence_level"] == "high"
    assert result["supported_claims"] == 1
    assert result["total_claims"] == 1

    assert result["sources"][0]["chunk_id"] == "chunk-1"
    assert result["sources"][0]["document_id"] == "doc-1"


def test_rag_safe_refusal_returns_zero_reliability(monkeypatch):
    service = RAGService()

    monkeypatch.setattr(
        "app.services.rag_service.retrieval_service.search",
        lambda query, limit, score_threshold: [],
    )

    result = service.answer(
        query="Who built the Eiffel Tower?",
        limit=5,
        score_threshold=0.5,
    )

    assert result["reliability_score"] == 0.0
    assert result["claim_support_score"] == 0.0
    assert result["retrieval_score"] == 0.0
    assert result["reliability_status"] == "safe_refusal"
    assert result["confidence_level"] == "low"
    assert result["claims"] == []
    assert result["supported_claims"] == 0
    assert result["total_claims"] == 0
    assert result["sources"] == []


def test_rag_passes_retrieval_score_to_reliability(monkeypatch):
    service = RAGService()

    monkeypatch.setattr(
        "app.services.rag_service.retrieval_service.search",
        lambda query, limit, score_threshold: [
            type(
                "Result",
                (),
                {
                    "score": 0.65,
                    "payload": {
                        "content": "Test evidence.",
                        "title": "Test Document",
                        "document_id": "doc-1",
                        "chunk_id": "chunk-1",
                    },
                },
            )()
        ],
    )

    monkeypatch.setattr(
        "app.services.rag_service.llm_service.generate",
        lambda prompt: "Test answer.",
    )

    captured = {}

    def fake_analyze(
        answer,
        evidence,
        retrieval_score,
    ):
        captured["answer"] = answer
        captured["evidence"] = evidence
        captured["retrieval_score"] = retrieval_score

        return {
            "reliability_score": 0.69,
            "claim_support_score": 0.7,
            "retrieval_score": retrieval_score,
            "reliability_status": "partially_supported",
            "confidence_level": "medium",
            "claims": [],
            "supported_claims": 0,
            "total_claims": 0,
        }

    monkeypatch.setattr(
        "app.services.rag_service.reliability_service.analyze",
        fake_analyze,
    )

    result = service.answer(
        query="Test question",
        limit=5,
        score_threshold=0.5,
    )

    assert captured["answer"] == "Test answer."
    assert "Test evidence." in captured["evidence"]
    assert captured["retrieval_score"] == 0.65

    assert result["reliability_score"] == 0.69
    assert result["retrieval_score"] == 0.65
    assert result["reliability_status"] == "partially_supported"
    assert result["confidence_level"] == "medium"