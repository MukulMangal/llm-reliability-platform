from app.services.reliability_service import reliability_service


def test_evaluation_supported_claim(monkeypatch):
    monkeypatch.setattr(
        "app.services.reliability_service.claim_service.extract_claims",
        lambda answer: [
            "Diabetes may increase the risk of cardiovascular disease."
        ],
    )

    monkeypatch.setattr(
        "app.services.reliability_service.verification_service.verify_claim",
        lambda claim, evidence: {
            "supported": True,
            "evidence": evidence,
        },
    )

    result = reliability_service.analyze(
        answer="Diabetes may increase the risk of cardiovascular disease.",
        evidence=(
            "Diabetes is a chronic disease that may "
            "increase the risk of cardiovascular disease."
        ),
        retrieval_score=0.8,
    )

    assert result["claim_support_score"] == 1.0
    assert result["reliability_status"] == "highly_supported"
    assert result["confidence_level"] == "high"


def test_evaluation_partially_supported_claims(monkeypatch):
    monkeypatch.setattr(
        "app.services.reliability_service.claim_service.extract_claims",
        lambda answer: [
            "Diabetes may increase the risk of cardiovascular disease.",
            "Diabetes causes kidney failure.",
        ],
    )

    def fake_verify_claim(claim, evidence):
        return {
            "supported": claim
            == "Diabetes may increase the risk of cardiovascular disease.",
            "evidence": evidence
            if claim
            == "Diabetes may increase the risk of cardiovascular disease."
            else None,
        }

    monkeypatch.setattr(
        "app.services.reliability_service.verification_service.verify_claim",
        fake_verify_claim,
    )

    result = reliability_service.analyze(
        answer=(
            "Diabetes may increase the risk of cardiovascular disease. "
            "Diabetes causes kidney failure."
        ),
        evidence=(
            "Diabetes is a chronic disease that may "
            "increase the risk of cardiovascular disease."
        ),
        retrieval_score=0.8,
    )

    assert result["claim_support_score"] == 0.5
    assert result["supported_claims"] == 1
    assert result["total_claims"] == 2
    assert result["reliability_status"] == "partially_supported"
    assert result["confidence_level"] == "medium"


def test_evaluation_unsupported_claim(monkeypatch):
    monkeypatch.setattr(
        "app.services.reliability_service.claim_service.extract_claims",
        lambda answer: ["Diabetes causes kidney failure."],
    )

    monkeypatch.setattr(
        "app.services.reliability_service.verification_service.verify_claim",
        lambda claim, evidence: {
            "supported": False,
            "evidence": None,
        },
    )

    result = reliability_service.analyze(
        answer="Diabetes causes kidney failure.",
        evidence=(
            "Diabetes is a chronic disease that may "
            "increase the risk of cardiovascular disease."
        ),
        retrieval_score=0.8,
    )

    assert result["claim_support_score"] == 0.0
    assert result["reliability_status"] == "unsupported"
    assert result["confidence_level"] == "low"


def test_evaluation_empty_claims(monkeypatch):
    monkeypatch.setattr(
        "app.services.reliability_service.claim_service.extract_claims",
        lambda answer: [],
    )

    result = reliability_service.analyze(
        answer="",
        evidence="Some evidence.",
        retrieval_score=0.8,
    )

    assert result["claim_support_score"] == 0.0
    assert result["supported_claims"] == 0
    assert result["total_claims"] == 0
    assert result["claims"] == []
    assert result["reliability_status"] == "unsupported"
    assert result["confidence_level"] == "low"


def test_evaluation_retrieval_score_is_clamped():
    verified_claims = [
        {
            "text": "Test claim.",
            "supported": True,
            "evidence": "Test evidence.",
        }
    ]

    result = reliability_service.calculate_score(
        verified_claims=verified_claims,
        retrieval_score=1.5,
    )

    assert result["retrieval_score"] == 1.0
    assert result["reliability_score"] == 1.0
    assert result["confidence_level"] == "high"


def test_evaluation_low_retrieval_score_reduces_reliability():
    verified_claims = [
        {
            "text": "Test claim.",
            "supported": True,
            "evidence": "Test evidence.",
        }
    ]

    result = reliability_service.calculate_score(
        verified_claims=verified_claims,
        retrieval_score=0.2,
    )

    assert result["claim_support_score"] == 1.0
    assert result["retrieval_score"] == 0.2
    assert result["reliability_score"] == 0.76
    assert result["confidence_level"] == "medium"


def test_evaluation_supported_claim_with_zero_retrieval():
    verified_claims = [
        {
            "text": "Test claim.",
            "supported": True,
            "evidence": "Test evidence.",
        }
    ]

    result = reliability_service.calculate_score(
        verified_claims=verified_claims,
        retrieval_score=0.0,
    )

    assert result["claim_support_score"] == 1.0
    assert result["retrieval_score"] == 0.0
    assert result["reliability_score"] == 0.7
    assert result["reliability_status"] == "highly_supported"
    assert result["confidence_level"] == "medium"


def test_evaluation_unsupported_claim_with_perfect_retrieval():
    verified_claims = [
        {
            "text": "Test claim.",
            "supported": False,
            "evidence": None,
        }
    ]

    result = reliability_service.calculate_score(
        verified_claims=verified_claims,
        retrieval_score=1.0,
    )

    assert result["claim_support_score"] == 0.0
    assert result["retrieval_score"] == 1.0
    assert result["reliability_score"] == 0.3
    assert result["reliability_status"] == "unsupported"
    assert result["confidence_level"] == "low"


def test_evaluation_half_supported_claims():
    verified_claims = [
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
    ]

    result = reliability_service.calculate_score(
        verified_claims=verified_claims,
        retrieval_score=0.8,
    )

    assert result["claim_support_score"] == 0.5
    assert result["retrieval_score"] == 0.8
    assert result["reliability_score"] == 0.59
    assert result["reliability_status"] == "partially_supported"
    assert result["confidence_level"] == "medium"


def test_evaluation_negative_retrieval_score_is_clamped():
    verified_claims = [
        {
            "text": "Test claim.",
            "supported": True,
            "evidence": "Test evidence.",
        }
    ]

    result = reliability_service.calculate_score(
        verified_claims=verified_claims,
        retrieval_score=-0.5,
    )

    assert result["retrieval_score"] == 0.0
    assert result["reliability_score"] == 0.7
    assert result["confidence_level"] == "medium"