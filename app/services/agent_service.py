import json

from app.services.agent_failure_service import agent_failure_service
from app.services.agent_guardrails import agent_guardrails
from app.services.agent_reliability_service import agent_reliability_service
from app.services.agent_tools import agent_tools
from app.services.llm_service import llm_service


class AgentService:
    """
    Orchestrates the Razorpay AI agent.

    The LLM handles natural-language intent detection.
    Deterministic guardrails validate the request.
    Agent tools execute explicitly allowed operations.
    Reliability evaluation verifies the returned API result.
    """

    ALLOWED_INTENTS = {
        "create_payment_link",
        "fetch_payment",
        "fetch_payment_link",
        "refund_payment",
        "unsupported",
    }

    def route(self, user_query: str) -> dict:
        """
        Convert a natural-language request into a structured intent.
        """
        if not user_query.strip():
            return {
                "intent": "unsupported",
                "parameters": {},
            }

        prompt = f"""
You are an intent router for a Razorpay payment operations agent.

Determine what operation the user is requesting.

Allowed intents:
- create_payment_link
- fetch_payment
- fetch_payment_link
- refund_payment
- unsupported

Extract only the parameters required for the selected operation.

For create_payment_link:
- amount_in_paise: integer amount in paise
- description: payment description
- currency: currency code, default INR

For fetch_payment:
- payment_id: Razorpay payment ID

For fetch_payment_link:
- payment_link_id: Razorpay payment link ID

For refund_payment:
- payment_id: Razorpay payment ID
- amount_in_paise: optional integer amount in paise

If a required parameter is missing, do not invent it.
Return null for that parameter.

Return ONLY valid JSON:

{{
    "intent": "one_allowed_intent",
    "parameters": {{
        "amount_in_paise": null,
        "description": null,
        "currency": null,
        "payment_id": null,
        "payment_link_id": null
    }}
}}

User request:
{user_query}
"""

        response = llm_service.generate(prompt)
        parsed = self._parse_response(response)

        intent = parsed.get("intent")
        parameters = parsed.get("parameters", {})

        if intent not in self.ALLOWED_INTENTS:
            return {
                "intent": "unsupported",
                "parameters": {},
            }

        if not isinstance(parameters, dict):
            parameters = {}

        return {
            "intent": intent,
            "parameters": parameters,
        }

    def execute(self, user_query: str) -> dict:
        """
        Route, validate, execute, and evaluate an agent request.
        """
        try:
            routed = self.route(user_query)

            intent = routed["intent"]
            parameters = routed["parameters"]

            valid, reason = agent_guardrails.validate(
                intent,
                parameters,
            )

            if not valid:
                return {
                    "success": False,
                    "operation": intent,
                    "status": "validation_failed",
                    "message": reason,
                }

            result = self._execute_tool(
                intent,
                parameters,
            )

            reliability = agent_reliability_service.evaluate(
                intent,
                result,
            )

            return {
                "success": True,
                "operation": intent,
                "status": "completed",
                "result": result,
                "reliability": reliability,
            }

        except Exception as exc:
            operation = "unknown"

            if "intent" in locals():
                operation = intent

            return agent_failure_service.handle(
                operation,
                exc,
            )

    @staticmethod
    def _execute_tool(
        intent: str,
        parameters: dict,
    ) -> dict:
        """
        Execute only an explicitly allowed agent tool.
        """
        if intent == "create_payment_link":
            return agent_tools.create_payment_link(
                amount=parameters["amount_in_paise"],
                description=parameters["description"],
                currency=parameters.get("currency") or "INR",
            )

        if intent == "fetch_payment":
            return agent_tools.fetch_payment(
                parameters["payment_id"],
            )

        if intent == "fetch_payment_link":
            return agent_tools.fetch_payment_link(
                parameters["payment_link_id"],
            )

        if intent == "refund_payment":
            return agent_tools.refund_payment(
                payment_id=parameters["payment_id"],
                amount=parameters.get("amount_in_paise"),
            )

        raise ValueError("Unsupported agent operation.")

    @staticmethod
    def _parse_response(response: str) -> dict:
        """
        Parse JSON returned by the LLM.
        """
        cleaned = response.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Agent returned an invalid intent response."
            ) from exc

        if not isinstance(parsed, dict):
            raise ValueError(
                "Agent intent response must be a JSON object."
            )

        return parsed


agent_service = AgentService()