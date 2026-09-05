from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.documents import router as document_router
from app.api.query import router as query_router
from app.schemas.query import QueryResponse


app = FastAPI()

app.include_router(document_router)
app.include_router(query_router)

client = TestClient(app)


def test_query_rejects_empty_query():
    response = client.post(
        "/query/",
        json={
            "query": "",
            "limit": 5,
            "score_threshold": 0.5,
        },
    )

    assert response.status_code == 422


def test_query_rejects_invalid_limit():
    response = client.post(
        "/query/",
        json={
            "query": "What is diabetes?",
            "limit": 0,
            "score_threshold": 0.5,
        },
    )

    assert response.status_code == 422


def test_query_rejects_invalid_score_threshold():
    response = client.post(
        "/query/",
        json={
            "query": "What is diabetes?",
            "limit": 5,
            "score_threshold": 1.5,
        },
    )

    assert response.status_code == 422


def test_document_rejects_empty_title():
    response = client.post(
        "/knowledge-bases/kb_test/text",
        json={
            "title": "",
            "content": "Some document content.",
        },
    )

    assert response.status_code == 422


def test_document_rejects_empty_content():
    response = client.post(
        "/knowledge-bases/kb_test/text",
        json={
            "title": "Test Document",
            "content": "",
        },
    )

    assert response.status_code == 422


def test_document_rejects_oversized_title():
    response = client.post(
        "/knowledge-bases/kb_test/text",
        json={
            "title": "A" * 201,
            "content": "Some document content.",
        },
    )

    assert response.status_code == 422


def test_query_returns_reliability_response(monkeypatch):
    expected_response = {
        "query": "What is diabetes?",
        "answer": "Diabetes affects blood glucose levels.",
        "reliability_score": 0.92,
        "claim_support_score": 1.0,
        "retrieval_score": 0.8,
        "reliability_status": "highly_supported",
        "confidence_level": "high",
        "claims": [
            {
                "text": "Diabetes affects blood glucose levels.",
                "supported": True,
                "evidence": "Diabetes affects blood glucose levels.",
            }
        ],
        "supported_claims": 1,
        "total_claims": 1,
        "sources": [
            {
                "score": 0.8,
                "chunk_id": "chunk_001",
                "document_id": "doc_001",
                "content": "Diabetes affects blood glucose levels.",
            }
        ],
    }

    def fake_answer(
        query,
        limit=5,
        score_threshold=0.5,
    ):
        assert query == "What is diabetes?"
        assert limit == 5
        assert score_threshold == 0.5

        return expected_response

    monkeypatch.setattr(
        "app.api.query.rag_service.answer",
        fake_answer,
    )

    response = client.post(
        "/query/",
        json={
            "query": "What is diabetes?",
            "limit": 5,
            "score_threshold": 0.5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == expected_response["query"]
    assert data["answer"] == expected_response["answer"]
    assert data["reliability_score"] == expected_response["reliability_score"]
    assert data["claim_support_score"] == expected_response["claim_support_score"]
    assert data["retrieval_score"] == expected_response["retrieval_score"]
    assert data["reliability_status"] == expected_response["reliability_status"]
    assert data["confidence_level"] == expected_response["confidence_level"]
    assert data["claims"] == expected_response["claims"]
    assert data["supported_claims"] == expected_response["supported_claims"]
    assert data["total_claims"] == expected_response["total_claims"]
    assert data["sources"] == expected_response["sources"]


def test_query_response_rejects_invalid_reliability_status():
    response_data = {
        "query": "What is diabetes?",
        "answer": "Diabetes affects blood glucose levels.",
        "reliability_score": 0.92,
        "claim_support_score": 1.0,
        "retrieval_score": 0.8,
        "reliability_status": "invalid_status",
        "confidence_level": "high",
        "claims": [],
        "supported_claims": 0,
        "total_claims": 0,
        "sources": [],
    }

    try:
        QueryResponse.model_validate(response_data)
        assert False
    except ValueError:
        assert True


def test_query_response_rejects_invalid_confidence_level():
    response_data = {
        "query": "What is diabetes?",
        "answer": "Diabetes affects blood glucose levels.",
        "reliability_score": 0.92,
        "claim_support_score": 1.0,
        "retrieval_score": 0.8,
        "reliability_status": "highly_supported",
        "confidence_level": "very_high",
        "claims": [],
        "supported_claims": 0,
        "total_claims": 0,
        "sources": [],
    }

    try:
        QueryResponse.model_validate(response_data)
        assert False
    except ValueError:
        assert True