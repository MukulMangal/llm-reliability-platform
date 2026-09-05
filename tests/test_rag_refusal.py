from app.services.rag_service import RAGService


def test_rag_safe_refusal_when_no_results(monkeypatch):
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

    assert result["answer"] == (
        "I could not find relevant information "
        "in the knowledge base."
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


def test_rag_safe_refusal_when_llm_cannot_answer(monkeypatch):
    service = RAGService()

    monkeypatch.setattr(
        "app.services.rag_service.retrieval_service.search",
        lambda query, limit, score_threshold: [
            type(
                "Result",
                (),
                {
                    "score": 0.7,
                    "payload": {
                        "content": (
                            "Diabetes affects blood glucose levels."
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
            "Based on the provided context, "
            "there is no information about a treatment."
        ),
    )

    reliability_called = False

    def fake_analyze(
        answer,
        evidence,
        retrieval_score,
    ):
        nonlocal reliability_called
        reliability_called = True

        return {
            "reliability_score": 0.0,
            "claim_support_score": 0.0,
            "retrieval_score": retrieval_score,
            "reliability_status": "safe_refusal",
            "confidence_level": "low",
            "claims": [],
            "supported_claims": 0,
            "total_claims": 0,
        }

    monkeypatch.setattr(
        "app.services.rag_service.reliability_service.analyze",
        fake_analyze,
    )

    result = service.answer(
        query="What treatment cures diabetes?",
        limit=5,
        score_threshold=0.5,
    )

    assert result["reliability_score"] == 0.0
    assert result["claim_support_score"] == 0.0
    assert result["retrieval_score"] == 0.7
    assert result["reliability_status"] == "safe_refusal"
    assert result["confidence_level"] == "low"
    assert result["claims"] == []
    assert result["supported_claims"] == 0
    assert result["total_claims"] == 0

    assert reliability_called is False

    assert len(result["sources"]) == 1
    assert result["sources"][0]["chunk_id"] == "chunk-1"


def test_rag_refusal_does_not_generate_claims(monkeypatch):
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
        lambda prompt: (
            "Based on the provided context, "
            "there is no information about this."
        ),
    )

    reliability_called = False

    def fake_analyze(
        answer,
        evidence,
        retrieval_score,
    ):
        nonlocal reliability_called
        reliability_called = True

        return {
            "reliability_score": 0.0,
            "claim_support_score": 0.0,
            "retrieval_score": retrieval_score,
            "reliability_status": "safe_refusal",
            "confidence_level": "low",
            "claims": [],
            "supported_claims": 0,
            "total_claims": 0,
        }

    monkeypatch.setattr(
        "app.services.rag_service.reliability_service.analyze",
        fake_analyze,
    )

    result = service.answer(
        query="Unknown question",
        limit=5,
        score_threshold=0.5,
    )

    assert result["reliability_status"] == "safe_refusal"
    assert result["confidence_level"] == "low"
    assert result["claims"] == []
    assert result["supported_claims"] == 0
    assert result["total_claims"] == 0
    assert reliability_called is False