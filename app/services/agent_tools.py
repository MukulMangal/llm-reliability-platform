from app.services.razorpay_service import razorpay_service


class AgentTools:
    """
    Explicit set of actions available to the AI agent.

    The agent can only perform operations exposed here.
    """

    def create_payment_link(
        self,
        amount: int,
        description: str,
        currency: str = "INR",
    ) -> dict:
        """
        Create a Razorpay payment link.
        """
        return razorpay_service.create_payment_link(
            amount=amount,
            description=description,
            currency=currency,
        )

    def fetch_payment(self, payment_id: str) -> dict:
        """
        Fetch a Razorpay payment.
        """
        return razorpay_service.fetch_payment(payment_id)

    def fetch_payment_link(self, payment_link_id: str) -> dict:
        """
        Fetch a Razorpay payment link.
        """
        return razorpay_service.fetch_payment_link(payment_link_id)

    def refund_payment(
        self,
        payment_id: str,
        amount: int | None = None,
    ) -> dict:
        """
        Verify payment state and refund only captured payments.
        """
        payment = razorpay_service.fetch_payment(payment_id)

        payment_status = payment.get("status")

        if payment_status != "captured":
            raise ValueError(
                "Refund is only allowed for captured payments."
            )

        payment_amount = payment.get("amount")

        if amount is not None:
            if not isinstance(payment_amount, int):
                raise ValueError(
                    "Unable to verify the original payment amount."
                )

            if amount > payment_amount:
                raise ValueError(
                    "Refund amount cannot exceed the captured payment amount."
                )

        return razorpay_service.refund_payment(
            payment_id=payment_id,
            amount=amount,
        )


agent_tools = AgentTools()