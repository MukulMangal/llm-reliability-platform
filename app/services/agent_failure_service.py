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
        Return a safe message without exposing internal API details.
        """
        message = str(error).lower()

        if "unable to connect" in message:
            return (
                "Unable to connect to Razorpay. "
                "Please try again."
            )

        if "request failed" in message:
            return (
                "Razorpay could not complete the requested operation."
            )

        return "The Razorpay operation could not be completed."


agent_failure_service = AgentFailureService()