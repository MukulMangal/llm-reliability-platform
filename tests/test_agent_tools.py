from unittest.mock import patch

import pytest

from app.services.agent_tools import agent_tools


def test_refund_requires_captured_payment():
    payment = {
        "id": "pay_test123",
        "status": "authorized",
        "amount": 50000,
    }

    with patch(
        "app.services.agent_tools.razorpay_service.fetch_payment",
        return_value=payment,
    ), patch(
        "app.services.agent_tools.razorpay_service.refund_payment",
    ) as mock_refund:
        with pytest.raises(
            ValueError,
            match="only allowed for captured payments",
        ):
            agent_tools.refund_payment("pay_test123")

        mock_refund.assert_not_called()


def test_refund_rejects_amount_greater_than_payment():
    payment = {
        "id": "pay_test123",
        "status": "captured",
        "amount": 50000,
    }

    with patch(
        "app.services.agent_tools.razorpay_service.fetch_payment",
        return_value=payment,
    ), patch(
        "app.services.agent_tools.razorpay_service.refund_payment",
    ) as mock_refund:
        with pytest.raises(
            ValueError,
            match="cannot exceed",
        ):
            agent_tools.refund_payment(
                "pay_test123",
                amount=60000,
            )

        mock_refund.assert_not_called()


def test_captured_payment_can_be_refunded():
    payment = {
        "id": "pay_test123",
        "status": "captured",
        "amount": 50000,
    }

    refund_response = {
        "id": "rfnd_test123",
        "payment_id": "pay_test123",
        "amount": 50000,
    }

    with patch(
        "app.services.agent_tools.razorpay_service.fetch_payment",
        return_value=payment,
    ), patch(
        "app.services.agent_tools.razorpay_service.refund_payment",
        return_value=refund_response,
    ) as mock_refund:
        result = agent_tools.refund_payment("pay_test123")

        assert result == refund_response

        mock_refund.assert_called_once_with(
            payment_id="pay_test123",
            amount=None,
        )


def test_partial_refund_cannot_exceed_payment_amount():
    payment = {
        "id": "pay_test123",
        "status": "captured",
        "amount": 50000,
    }

    refund_response = {
        "id": "rfnd_test123",
        "payment_id": "pay_test123",
        "amount": 20000,
    }

    with patch(
        "app.services.agent_tools.razorpay_service.fetch_payment",
        return_value=payment,
    ), patch(
        "app.services.agent_tools.razorpay_service.refund_payment",
        return_value=refund_response,
    ) as mock_refund:
        result = agent_tools.refund_payment(
            "pay_test123",
            amount=20000,
        )

        assert result == refund_response

        mock_refund.assert_called_once_with(
            payment_id="pay_test123",
            amount=20000,
        )