class AgentGuardrails:
    """
    Deterministic validation layer for agent actions.

    The LLM may identify the user's intent and extract parameters,
    but this layer decides whether the requested operation has
    sufficient and valid parameters to proceed.
    """

    ALLOWED_INTENTS = {
        "create_payment_link",
        "fetch_payment",
        "fetch_payment_link",
        "refund_payment",
        "unsupported",
    }

    def validate(
        self,
        intent: str,
        parameters: dict,
    ) -> tuple[bool, str]:
        """
        Validate an agent action before it can reach Razorpay.

        Returns:
            (True, "") when the action is valid.
            (False, reason) when the action must be rejected.
        """
        if intent not in self.ALLOWED_INTENTS:
            return False, "Unsupported agent operation."

        if intent == "unsupported":
            return False, "The requested operation is not supported."

        if not isinstance(parameters, dict):
            return False, "Invalid agent parameters."

        if intent == "create_payment_link":
            return self._validate_create_payment_link(parameters)

        if intent == "fetch_payment":
            return self._validate_identifier(
                parameters.get("payment_id"),
                "payment ID",
            )

        if intent == "fetch_payment_link":
            return self._validate_identifier(
                parameters.get("payment_link_id"),
                "payment link ID",
            )

        if intent == "refund_payment":
            return self._validate_refund(parameters)

        return False, "Unsupported agent operation."

    @staticmethod
    def _validate_identifier(
        identifier: object,
        name: str,
    ) -> tuple[bool, str]:
        """
        Validate a Razorpay resource identifier.
        """
        if not isinstance(identifier, str) or not identifier.strip():
            return False, f"A valid {name} is required."

        return True, ""

    @staticmethod
    def _validate_create_payment_link(
        parameters: dict,
    ) -> tuple[bool, str]:
        """
        Validate payment-link creation parameters.
        """
        amount = parameters.get("amount_in_paise")
        description = parameters.get("description")
        currency = parameters.get("currency")

        if not isinstance(amount, int) or isinstance(amount, bool):
            return False, "A valid payment amount is required."

        if amount <= 0:
            return False, "Payment amount must be greater than zero."

        if not isinstance(description, str) or not description.strip():
            return False, "A payment description is required."

        if currency is not None:
            if not isinstance(currency, str) or not currency.strip():
                return False, "Currency must be a valid currency code."

        return True, ""

    @staticmethod
    def _validate_refund(
        parameters: dict,
    ) -> tuple[bool, str]:
        """
        Validate refund parameters.

        Payment eligibility will be verified against Razorpay
        separately before the refund is executed.
        """
        payment_id = parameters.get("payment_id")
        amount = parameters.get("amount_in_paise")

        valid_payment_id, reason = AgentGuardrails._validate_identifier(
            payment_id,
            "payment ID",
        )

        if not valid_payment_id:
            return False, reason

        if amount is not None:
            if not isinstance(amount, int) or isinstance(amount, bool):
                return False, "Refund amount must be a valid integer."

            if amount <= 0:
                return False, "Refund amount must be greater than zero."

        return True, ""


agent_guardrails = AgentGuardrails()