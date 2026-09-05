from app.services.agent_guardrails import agent_guardrails


def test_valid_create_payment_link():
    valid, reason = agent_guardrails.validate(
        "create_payment_link",
        {
            "amount_in_paise": 50000,
            "description": "Test payment",
            "currency": "INR",
        },
    )

    assert valid is True
    assert reason == ""


def test_create_payment_link_rejects_invalid_amount():
    valid, reason = agent_guardrails.validate(
        "create_payment_link",
        {
            "amount_in_paise": 0,
            "description": "Test payment",
            "currency": "INR",
        },
    )

    assert valid is False
    assert "amount" in reason.lower()


def test_create_payment_link_rejects_missing_description():
    valid, reason = agent_guardrails.validate(
        "create_payment_link",
        {
            "amount_in_paise": 50000,
            "description": "",
            "currency": "INR",
        },
    )

    assert valid is False
    assert "description" in reason.lower()


def test_fetch_payment_requires_payment_id():
    valid, reason = agent_guardrails.validate(
        "fetch_payment",
        {},
    )

    assert valid is False
    assert "payment id" in reason.lower()


def test_fetch_payment_link_requires_payment_link_id():
    valid, reason = agent_guardrails.validate(
        "fetch_payment_link",
        {},
    )

    assert valid is False
    assert "payment link id" in reason.lower()


def test_refund_requires_payment_id():
    valid, reason = agent_guardrails.validate(
        "refund_payment",
        {
            "amount_in_paise": 10000,
        },
    )

    assert valid is False
    assert "payment id" in reason.lower()


def test_refund_rejects_invalid_amount():
    valid, reason = agent_guardrails.validate(
        "refund_payment",
        {
            "payment_id": "pay_test123",
            "amount_in_paise": 0,
        },
    )

    assert valid is False
    assert "amount" in reason.lower()


def test_unsupported_intent_is_rejected():
    valid, reason = agent_guardrails.validate(
        "delete_account",
        {},
    )

    assert valid is False
    assert "unsupported" in reason.lower()


def test_unsupported_operation_is_rejected():
    valid, reason = agent_guardrails.validate(
        "unsupported",
        {},
    )

    assert valid is False
    assert "not supported" in reason.lower()