import pytest

from app.services.agent_failure_service import agent_failure_service


def test_validation_error_returns_validation_failed():
    result = agent_failure_service.handle(
        "refund_payment",
        ValueError("Payment ID is required."),
    )

    assert result["success"] is False
    assert result["operation"] == "refund_payment"
    assert result["status"] == "validation_failed"
    assert result["message"] == "Payment ID is required."


def test_razorpay_connection_error_is_safe():
    result = agent_failure_service.handle(
        "fetch_payment",
        RuntimeError("Unable to connect to Razorpay API"),
    )

    assert result["success"] is False
    assert result["status"] == "operation_failed"
    assert "Unable to connect to Razorpay" in result["message"]


def test_razorpay_api_error_does_not_leak_details():
    result = agent_failure_service.handle(
        "refund_payment",
        RuntimeError(
            "Razorpay API request failed with status 401 "
            "secret_key=super_secret_value"
        ),
    )

    assert result["success"] is False
    assert result["status"] == "operation_failed"
    assert "super_secret_value" not in result["message"]
    assert "401" not in result["message"]


def test_unknown_error_returns_generic_message():
    result = agent_failure_service.handle(
        "create_payment_link",
        Exception("Internal database secret"),
    )

    assert result["success"] is False
    assert result["status"] == "operation_failed"
    assert result["message"] == "The operation could not be completed."