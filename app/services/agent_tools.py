from app.services.razorpay_service import razorpay_service


class AgentTools:
    """
    Deterministic execution layer for Razorpay operations.

    These methods are the only financial actions exposed to the AI agent.
    The LLM cannot directly call Razorpay or dynamically select arbitrary
    API endpoints.
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
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise ValueError(
                "Payment link amount must be an integer in paise."
            )

        if amount <= 0:
            raise ValueError(
                "Payment link amount must be greater than zero."
            )

        if not isinstance(description, str) or not description.strip():
            raise ValueError(
                "Payment link description cannot be empty."
            )

        if not isinstance(currency, str) or not currency.strip():
            raise ValueError(
                "Payment currency cannot be empty."
            )

        normalized_currency = currency.strip().upper()

        return razorpay_service.create_payment_link(
            amount=amount,
            description=description.strip(),
            currency=normalized_currency,
        )

    def fetch_payment(
        self,
        payment_id: str,
    ) -> dict:
        """
        Fetch a Razorpay payment by its payment ID.
        """
        self._validate_identifier(
            payment_id,
            "payment ID",
        )

        return razorpay_service.fetch_payment(
            payment_id.strip(),
        )

    def fetch_payment_link(
        self,
        payment_link_id: str,
    ) -> dict:
        """
        Fetch a Razorpay payment link by its payment-link ID.
        """
        self._validate_identifier(
            payment_link_id,
            "payment link ID",
        )

        return razorpay_service.fetch_payment_link(
            payment_link_id.strip(),
        )

    def refund_payment(
        self,
        payment_id: str,
        amount: int | None = None,
    ) -> dict:
        """
        Refund a captured Razorpay payment.

        Before issuing a refund request, the original payment is fetched
        and its state and amount are deterministically verified.

        This prevents the AI agent from blindly issuing a financial action.
        """
        self._validate_identifier(
            payment_id,
            "payment ID",
        )

        if amount is not None:
            if not isinstance(amount, int) or isinstance(amount, bool):
                raise ValueError(
                    "Refund amount must be an integer in paise."
                )

            if amount <= 0:
                raise ValueError(
                    "Refund amount must be greater than zero."
                )

        payment = razorpay_service.fetch_payment(
            payment_id.strip(),
        )

        payment_status = payment.get("status")

        if payment_status != "captured":
            raise ValueError(
                "Refund is only allowed for captured payments."
            )

        payment_amount = payment.get("amount")

        if not isinstance(payment_amount, int):
            raise ValueError(
                "Unable to verify the original payment amount."
            )

        if amount is not None and amount > payment_amount:
            raise ValueError(
                "Refund amount cannot exceed the captured payment amount."
            )

        return razorpay_service.refund_payment(
            payment_id=payment_id.strip(),
            amount=amount,
        )

    @staticmethod
    def _validate_identifier(
        identifier: str,
        label: str,
    ) -> None:
        """
        Validate identifiers before any Razorpay API request is made.
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError(
                f"A valid {label} is required."
            )


agent_tools = AgentTools()