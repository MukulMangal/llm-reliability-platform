import pytest
from pydantic import ValidationError

from app.schemas.document import DocumentCreate
from app.schemas.query import QueryRequest


def test_document_requires_content():
    with pytest.raises(ValidationError):
        DocumentCreate(
            title="Test Document",
            content="",
        )


def test_document_requires_title():
    with pytest.raises(ValidationError):
        DocumentCreate(
            title="",
            content="Some content",
        )


def test_document_title_has_max_length():
    with pytest.raises(ValidationError):
        DocumentCreate(
            title="A" * 201,
            content="Some content",
        )


def test_query_requires_text():
    with pytest.raises(ValidationError):
        QueryRequest(
            query="",
        )


def test_query_limit_cannot_be_zero():
    with pytest.raises(ValidationError):
        QueryRequest(
            query="test",
            limit=0,
        )


def test_query_limit_cannot_exceed_maximum():
    with pytest.raises(ValidationError):
        QueryRequest(
            query="test",
            limit=21,
        )


def test_score_threshold_must_be_between_zero_and_one():
    with pytest.raises(ValidationError):
        QueryRequest(
            query="test",
            score_threshold=1.5,
        )


def test_valid_query_request():
    request = QueryRequest(
        query="What is diabetes?",
        limit=5,
        score_threshold=0.5,
    )

    assert request.query == "What is diabetes?"
    assert request.limit == 5
    assert request.score_threshold == 0.5