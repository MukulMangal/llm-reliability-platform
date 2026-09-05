from app.services.reliability_service import reliability_service


def test_highly_supported_claims():
    result = reliability_service.calculate_score(
        verified_claims=[
            {
                "text": "Diabetes increases cardiovascular risk.",
                "supported": True,
                "evidence": "Diabetes increases cardiovascular risk.",
            }
        ],
        retrieval_score=0.8,
    )

    assert result["reliability_score"] == 0.94
    assert result["claim_support_score"] == 1.0
    assert result["retrieval_score"] == 0.8
    assert result["reliability_status"] == "highly_supported"
    assert result["confidence_level"] == "high"
    assert result["supported_claims"] == 1
    assert result["total_claims"] == 1


def test_partially_supported_claims():
    result = reliability_service.calculate_score(
        verified_claims=[
            {
                "text": "Supported claim.",
                "supported": True,
                "evidence": "Evidence.",
            },
            {
                "text": "Unsupported claim.",
                "supported": False,
                "evidence": None,
            },
        ],
        retrieval_score=0.8,
    )

    assert result["reliability_score"] == 0.59
    assert result["claim_support_score"] == 0.5
    assert result["reliability_score"] == 0.59
    assert result["reliability_status"] == "partially_supported"
    assert result["confidence_level"] == "medium"
    assert result["supported_claims"] == 1
    assert result["total_claims"] == 2


def test_unsupported_claims():
    result = reliability_service.calculate_score(
        verified_claims=[
            {
                "text": "Unsupported claim.",
                "supported": False,
                "evidence": None,
            }
        ],
        retrieval_score=0.8,
    )

    assert result["reliability_score"] == 0.24
    assert result["claim_support_score"] == 0.0
    assert result["reliability_status"] == "unsupported"
    assert result["confidence_level"] == "low"
    assert result["supported_claims"] == 0
    assert result["total_claims"] == 1


def test_empty_claims():
    result = reliability_service.calculate_score(
        verified_claims=[],
        retrieval_score=0.8,
    )

    assert result["reliability_score"] == 0.0
    assert result["claim_support_score"] == 0.0
    assert result["retrieval_score"] == 0.8
    assert result["reliability_status"] == "unsupported"
    assert result["confidence_level"] == "low"
    assert result["supported_claims"] == 0
    assert result["total_claims"] == 0


def test_retrieval_score_is_clamped():
    result = reliability_service.calculate_score(
        verified_claims=[
            {
                "text": "Supported claim.",
                "supported": True,
                "evidence": "Evidence.",
            }
        ],
        retrieval_score=1.5,
    )

    assert result["retrieval_score"] == 1.0
    assert result["reliability_score"] == 1.0