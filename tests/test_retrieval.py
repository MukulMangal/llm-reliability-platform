from types import SimpleNamespace

from app.services.retrieval_service import RetrievalService


def test_retrieval_removes_duplicate_content(monkeypatch):
    service = RetrievalService()

    results = [
        SimpleNamespace(
            score=0.9,
            payload={
                "chunk_id": "chunk_001",
                "document_id": "doc_001",
                "content": "Diabetes increases cardiovascular risk.",
            },
        ),
        SimpleNamespace(
            score=0.8,
            payload={
                "chunk_id": "chunk_002",
                "document_id": "doc_002",
                "content": "Diabetes increases cardiovascular risk.",
            },
        ),
        SimpleNamespace(
            score=0.7,
            payload={
                "chunk_id": "chunk_003",
                "document_id": "doc_003",
                "content": "Diabetes affects blood glucose levels.",
            },
        ),
    ]

    def fake_embed_text(text):
        return [0.1, 0.2, 0.3]

    def fake_search(
        embedding,
        limit=5,
        score_threshold=0.5,
    ):
        return results

    monkeypatch.setattr(
        "app.services.retrieval_service.embedding_service.embed_text",
        fake_embed_text,
    )

    monkeypatch.setattr(
        "app.services.retrieval_service.vector_repository.search",
        fake_search,
    )

    retrieved = service.search(
        query="What are the effects of diabetes?",
        limit=5,
        score_threshold=0.5,
    )

    assert len(retrieved) == 2

    assert retrieved[0].payload["chunk_id"] == "chunk_001"
    assert retrieved[1].payload["chunk_id"] == "chunk_003"


def test_retrieval_returns_requested_number_of_unique_results(
    monkeypatch,
):
    service = RetrievalService()

    results = [
        SimpleNamespace(
            score=0.95,
            payload={
                "chunk_id": "chunk_001",
                "document_id": "doc_001",
                "content": "Same content.",
            },
        ),
        SimpleNamespace(
            score=0.90,
            payload={
                "chunk_id": "chunk_002",
                "document_id": "doc_002",
                "content": "Same content.",
            },
        ),
        SimpleNamespace(
            score=0.85,
            payload={
                "chunk_id": "chunk_003",
                "document_id": "doc_003",
                "content": "Unique content one.",
            },
        ),
        SimpleNamespace(
            score=0.80,
            payload={
                "chunk_id": "chunk_004",
                "document_id": "doc_004",
                "content": "Unique content two.",
            },
        ),
        SimpleNamespace(
            score=0.75,
            payload={
                "chunk_id": "chunk_005",
                "document_id": "doc_005",
                "content": "Unique content three.",
            },
        ),
    ]

    def fake_embed_text(text):
        return [0.1, 0.2, 0.3]

    def fake_search(
        embedding,
        limit=5,
        score_threshold=0.5,
    ):
        assert limit == 6
        return results

    monkeypatch.setattr(
        "app.services.retrieval_service.embedding_service.embed_text",
        fake_embed_text,
    )

    monkeypatch.setattr(
        "app.services.retrieval_service.vector_repository.search",
        fake_search,
    )

    retrieved = service.search(
        query="test query",
        limit=2,
        score_threshold=0.5,
    )

    assert len(retrieved) == 2

    assert retrieved[0].payload["chunk_id"] == "chunk_001"
    assert retrieved[1].payload["chunk_id"] == "chunk_003"


def test_retrieval_preserves_score_order(monkeypatch):
    service = RetrievalService()

    results = [
        SimpleNamespace(
            score=0.95,
            payload={
                "chunk_id": "chunk_001",
                "document_id": "doc_001",
                "content": "Highest relevance.",
            },
        ),
        SimpleNamespace(
            score=0.85,
            payload={
                "chunk_id": "chunk_002",
                "document_id": "doc_002",
                "content": "Medium relevance.",
            },
        ),
        SimpleNamespace(
            score=0.70,
            payload={
                "chunk_id": "chunk_003",
                "document_id": "doc_003",
                "content": "Lower relevance.",
            },
        ),
    ]

    def fake_embed_text(text):
        return [0.1, 0.2, 0.3]

    def fake_search(
        embedding,
        limit=5,
        score_threshold=0.5,
    ):
        return results

    monkeypatch.setattr(
        "app.services.retrieval_service.embedding_service.embed_text",
        fake_embed_text,
    )

    monkeypatch.setattr(
        "app.services.retrieval_service.vector_repository.search",
        fake_search,
    )

    retrieved = service.search(
        query="test query",
        limit=3,
        score_threshold=0.5,
    )

    assert len(retrieved) == 3

    assert retrieved[0].score == 0.95
    assert retrieved[1].score == 0.85
    assert retrieved[2].score == 0.70


def test_retrieval_respects_score_threshold(monkeypatch):
    service = RetrievalService()

    results = [
        SimpleNamespace(
            score=0.90,
            payload={
                "chunk_id": "chunk_high",
                "document_id": "doc_high",
                "content": "High relevance content.",
            },
        ),
        SimpleNamespace(
            score=0.60,
            payload={
                "chunk_id": "chunk_medium",
                "document_id": "doc_medium",
                "content": "Medium relevance content.",
            },
        ),
    ]

    def fake_embed_text(text):
        return [0.1, 0.2, 0.3]

    def fake_search(
        embedding,
        limit=5,
        score_threshold=0.5,
    ):
        assert score_threshold == 0.8

        return [
            result
            for result in results
            if result.score >= score_threshold
        ]

    monkeypatch.setattr(
        "app.services.retrieval_service.embedding_service.embed_text",
        fake_embed_text,
    )

    monkeypatch.setattr(
        "app.services.retrieval_service.vector_repository.search",
        fake_search,
    )

    retrieved = service.search(
        query="test query",
        limit=5,
        score_threshold=0.8,
    )

    assert len(retrieved) == 1

    assert retrieved[0].payload["chunk_id"] == "chunk_high"
    assert retrieved[0].score == 0.90