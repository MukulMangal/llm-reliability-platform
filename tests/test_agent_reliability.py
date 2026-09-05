from app.services.agent_reliability_service import agent_reliability_service


def test_create_payment_link_with_complete_response_is_highly_reliable():
    result = agent_reliability_service.evaluate(
        "create_payment_link",
        {
            "id": "plink_test123",
            "short_url": "https://rzp.io/i/test123",
            "amount": 50000,
            "currency": "INR",
        },
    )

    assert result["reliability_score"] == 1.0
    assert result["reliability_status"] == "highly_supported"
    assert result["confidence_level"] == "high"


def test_payment_with_complete_response_is_highly_reliable():
    result = agent_reliability_service.evaluate(
        "fetch_payment",
        {
            "id": "pay_test123",
            "amount": 50000,
            "currency": "INR",
            "status": "captured",
        },
    )

    assert result["reliability_score"] == 1.0
    assert result["reliability_status"] == "highly_supported"
    assert result["confidence_level"] == "high"


def test_refund_with_complete_response_is_highly_reliable():
    result = agent_reliability_service.evaluate(
        "refund_payment",
        {
            "id": "rfnd_test123",
            "payment_id": "pay_test123",
            "amount": 50000,
        },
    )

    assert result["reliability_score"] == 1.0
    assert result["reliability_status"] == "highly_supported"
    assert result["confidence_level"] == "high"


def test_incomplete_response_is_partially_reliable():
    result = agent_reliability_service.evaluate(
        "fetch_payment",
        {
            "id": "pay_test123",
            "status": "captured",
        },
    )

    assert result["reliability_score"] == 0.5
    assert result["reliability_status"] == "partially_supported"
    assert result["confidence_level"] == "medium"


def test_invalid_result_is_unsupported():
    result = agent_reliability_service.evaluate(
        "fetch_payment",
        None,
    )

    assert result["reliability_score"] == 0.0
    assert result["reliability_status"] == "unsupported"
    assert result["confidence_level"] == "low"


def test_unknown_operation_is_unsupported():
    result = agent_reliability_service.evaluate(
        "delete_payment",
        {
            "id": "test123",
        },
    )

    assert result["reliability_score"] == 0.0
    assert result["reliability_status"] == "unsupported"
    assert result["confidence_level"] == "low"