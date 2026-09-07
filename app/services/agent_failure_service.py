class AgentFailureService:
    """
    Converts internal agent and Razorpay failures into safe,
    structured responses for the user.
    """

    def handle(
        self,
        operation: str,
        error: Exception,
    ) -> dict:
        """
        Convert an exception into a safe agent failure response.
        """

        if isinstance(error, ValueError):
            return {
                "success": False,
                "operation": operation,
                "status": "validation_failed",
                "message": str(error),
            }

        if isinstance(error, RuntimeError):
            return {
                "success": False,
                "operation": operation,
                "status": "operation_failed",
                "message": self._safe_runtime_message(error),
            }

        return {
            "success": False,
            "operation": operation,
            "status": "operation_failed",
            "message": "The operation could not be completed.",
        }

    @staticmethod
    def _safe_runtime_message(error: RuntimeError) -> str:
        """
        Return a safe user-facing message for infrastructure and
        Razorpay API failures.

        RazorpayService already extracts the API's user-facing
        description rather than exposing raw HTTP responses,
        credentials, or stack traces.
        """

        message = str(error).strip()

        if not message:
            return "The Razorpay operation could not be completed."

        lowered = message.lower()

        if "unable to connect" in lowered:
            return (
                "Unable to connect to Razorpay. "
                "Please try again."
            )

        if "razorpay api request failed with status" in lowered:
            return (
                "Razorpay could not complete the requested operation."
            )

        if "razorpay" in lowered:
            return message

        return (
            "The Razorpay operation could not be completed."
        )


agent_failure_service = AgentFailureService()