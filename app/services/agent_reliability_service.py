class AgentReliabilityService:
    """
    Deterministic reliability evaluation for Razorpay agent actions.

    Razorpay API responses are treated as the authoritative source
    of truth. No LLM is used to determine whether an API operation
    actually succeeded.
    """

    def evaluate(
        self,
        operation: str,
        result: dict,
    ) -> dict:
        """
        Evaluate the reliability of a completed agent operation.
        """
        if not isinstance(result, dict):
            return {
                "reliability_score": 0.0,
                "reliability_status": "unsupported",
                "confidence_level": "low",
            }

        if operation == "create_payment_link":
            return self._evaluate_payment_link(result)

        if operation == "fetch_payment":
            return self._evaluate_payment(result)

        if operation == "fetch_payment_link":
            return self._evaluate_payment_link(result)

        if operation == "refund_payment":
            return self._evaluate_refund(result)

        return {
            "reliability_score": 0.0,
            "reliability_status": "unsupported",
            "confidence_level": "low",
        }

    @staticmethod
    def _evaluate_payment_link(result: dict) -> dict:
        """
        Evaluate a Razorpay Payment Link response.
        """
        required_fields = {
            "id",
            "short_url",
            "amount",
            "currency",
        }

        if required_fields.issubset(result.keys()):
            return {
                "reliability_score": 1.0,
                "reliability_status": "highly_supported",
                "confidence_level": "high",
            }

        return {
            "reliability_score": 0.5,
            "reliability_status": "partially_supported",
            "confidence_level": "medium",
        }

    @staticmethod
    def _evaluate_payment(result: dict) -> dict:
        """
        Evaluate a Razorpay Payment response.
        """
        required_fields = {
            "id",
            "amount",
            "currency",
            "status",
        }

        if required_fields.issubset(result.keys()):
            return {
                "reliability_score": 1.0,
                "reliability_status": "highly_supported",
                "confidence_level": "high",
            }

        return {
            "reliability_score": 0.5,
            "reliability_status": "partially_supported",
            "confidence_level": "medium",
        }

    @staticmethod
    def _evaluate_refund(result: dict) -> dict:
        """
        Evaluate a Razorpay refund response.
        """
        required_fields = {
            "id",
            "payment_id",
            "amount",
        }

        if required_fields.issubset(result.keys()):
            return {
                "reliability_score": 1.0,
                "reliability_status": "highly_supported",
                "confidence_level": "high",
            }

        return {
            "reliability_score": 0.5,
            "reliability_status": "partially_supported",
            "confidence_level": "medium",
        }


agent_reliability_service = AgentReliabilityService()