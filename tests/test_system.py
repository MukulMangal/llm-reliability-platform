from fastapi.testclient import TestClient

from app.main import app


client = TestClient(
    app,
    raise_server_exceptions=False,
)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_info_endpoint():
    response = client.get("/info")

    assert response.status_code == 200

    data = response.json()

    assert data["project"] == "LLM Reliability Platform"
    assert data["version"] == "0.1.0"


def test_query_api_returns_reliability_fields(monkeypatch):
    expected_response = {
        "query": "What health risk is associated with diabetes?",
        "answer": (
            "Diabetes may increase the risk "
            "of cardiovascular disease."
        ),
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
                "evidence": "Diabetes evidence.",
            }
        ],
        "supported_claims": 1,
        "total_claims": 1,
        "sources": [
            {
                "score": 0.8,
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "content": "Diabetes evidence.",
            }
        ],
    }

    monkeypatch.setattr(
        "app.api.query.rag_service.answer",
        lambda query, limit, score_threshold: expected_response,
    )

    response = client.post(
        "/query/",
        json={
            "query": "What health risk is associated with diabetes?",
            "limit": 5,
            "score_threshold": 0.5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == (
        "What health risk is associated with diabetes?"
    )
    assert data["answer"] == (
        "Diabetes may increase the risk "
        "of cardiovascular disease."
    )

    assert data["reliability_score"] == 0.94
    assert data["claim_support_score"] == 1.0
    assert data["retrieval_score"] == 0.8
    assert data["reliability_status"] == "highly_supported"
    assert data["confidence_level"] == "high"

    assert len(data["claims"]) == 1
    assert data["supported_claims"] == 1
    assert data["total_claims"] == 1

    assert len(data["sources"]) == 1
    assert data["sources"][0]["chunk_id"] == "chunk-1"
    assert data["sources"][0]["document_id"] == "doc-1"


def test_query_api_returns_safe_refusal(monkeypatch):
    expected_response = {
        "query": "Who built the Eiffel Tower?",
        "answer": (
            "I could not find relevant information "
            "in the knowledge base."
        ),
        "reliability_score": 0.0,
        "claim_support_score": 0.0,
        "retrieval_score": 0.0,
        "reliability_status": "safe_refusal",
        "confidence_level": "low",
        "claims": [],
        "supported_claims": 0,
        "total_claims": 0,
        "sources": [],
    }

    monkeypatch.setattr(
        "app.api.query.rag_service.answer",
        lambda query, limit, score_threshold: expected_response,
    )

    response = client.post(
        "/query/",
        json={
            "query": "Who built the Eiffel Tower?",
            "limit": 5,
            "score_threshold": 0.5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reliability_score"] == 0.0
    assert data["claim_support_score"] == 0.0
    assert data["retrieval_score"] == 0.0
    assert data["reliability_status"] == "safe_refusal"
    assert data["confidence_level"] == "low"

    assert data["claims"] == []
    assert data["supported_claims"] == 0
    assert data["total_claims"] == 0
    assert data["sources"] == []


def test_query_api_handles_internal_error(monkeypatch):
    def raise_internal_error(
        query,
        limit,
        score_threshold,
    ):
        raise RuntimeError("Sensitive internal failure")

    monkeypatch.setattr(
        "app.api.query.rag_service.answer",
        raise_internal_error,
    )

    response = client.post(
        "/query/",
        json={
            "query": "Test question",
            "limit": 5,
            "score_threshold": 0.5,
        },
    )

    assert response.status_code == 500

    data = response.json()

    assert data["error"] == "internal_server_error"
    assert data["detail"] == "Internal Server Error"

    assert "Sensitive internal failure" not in response.text