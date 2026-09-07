import json
import re
from typing import Any

from app.services.activity_service import activity_service
from app.services.agent_failure_service import agent_failure_service
from app.services.agent_guardrails import agent_guardrails
from app.services.agent_reliability_service import agent_reliability_service
from app.services.agent_tools import agent_tools
from app.services.llm_service import llm_service


class AgentService:
    """
    Orchestrates the Razorpay AI payment operations agent.

    The LLM is responsible for natural-language intent detection and
    parameter extraction. Deterministic guardrails remain responsible
    for validating financial actions before execution.

    If the LLM router is temporarily unavailable, a narrow deterministic
    fallback handles only explicit, unambiguous operation patterns.
    The fallback never bypasses guardrails or directly executes actions.
    """

    ALLOWED_INTENTS = frozenset(
        {
            "create_payment_link",
            "fetch_payment",
            "fetch_payment_link",
            "refund_payment",
            "unsupported",
        }
    )

    ALLOWED_PARAMETERS = frozenset(
        {
            "amount_in_paise",
            "description",
            "currency",
            "payment_id",
            "payment_link_id",
        }
    )

    def route(self, user_query: str) -> dict:
        """
        Convert a natural-language request into a validated intent object.

        The LLM normally performs routing. If the LLM is unavailable,
        a narrow deterministic fallback handles explicit commands without
        bypassing downstream guardrails.
        """
        if not user_query or not user_query.strip():
            return self._unsupported_route()

        prompt = f"""
You are an intent router for a Razorpay payment operations agent.

Your ONLY responsibility is to identify the user's requested operation
and extract explicitly provided parameters.

Allowed intents:
- create_payment_link
- fetch_payment
- fetch_payment_link
- refund_payment
- unsupported

Parameter rules:

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

Critical rules:
1. Never invent missing parameters.
2. Use null when a parameter was not explicitly provided.
3. Do not infer a payment ID or payment link ID.
4. Do not execute any operation.
5. Do not return explanations.
6. Return ONLY valid JSON.
7. Use exactly the following structure.

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

        try:
            response = llm_service.generate(prompt)
            parsed = self._parse_response(response)

            intent = parsed.get("intent")

            if intent not in self.ALLOWED_INTENTS:
                return self._unsupported_route()

            parameters = parsed.get("parameters")

            if not isinstance(parameters, dict):
                parameters = {}

            return {
                "intent": intent,
                "parameters": self._normalize_parameters(parameters),
            }

        except Exception:
            fallback = self._deterministic_fallback(user_query)

            if fallback is not None:
                return fallback

            raise

    def execute(self, user_query: str) -> dict:
        """
        Route, validate, execute, evaluate, and audit a payment operation.
        """
        operation = "unknown"

        try:
            routed = self.route(user_query)

            operation = routed["intent"]
            parameters = routed["parameters"]

            valid, reason = agent_guardrails.validate(
                operation,
                parameters,
            )

            if not valid:
                response = {
                    "success": False,
                    "operation": operation,
                    "status": "validation_failed",
                    "message": reason,
                    "result": None,
                    "reliability": None,
                }

                activity_service.record(
                    user_query=user_query,
                    operation=operation,
                    status="validation_failed",
                    success=False,
                    message=reason,
                    result=None,
                    reliability=None,
                )

                return response

            result = self._execute_tool(
                operation,
                parameters,
            )

            reliability = agent_reliability_service.evaluate(
                operation,
                result,
            )

            response = {
                "success": True,
                "operation": operation,
                "status": "completed",
                "message": None,
                "result": result,
                "reliability": reliability,
            }

            activity_service.record(
                user_query=user_query,
                operation=operation,
                status="completed",
                success=True,
                message=None,
                result=result,
                reliability=reliability,
            )

            return response

        except Exception as exc:
            failure = agent_failure_service.handle(
                operation,
                exc,
            )

            activity_service.record(
                user_query=user_query,
                operation=failure.get("operation", operation),
                status=failure.get("status", "operation_failed"),
                success=False,
                message=failure.get("message"),
                result=failure.get("result"),
                reliability=failure.get("reliability"),
            )

            return failure

    @classmethod
    def _execute_tool(
        cls,
        intent: str,
        parameters: dict,
    ) -> dict:
        """
        Execute exactly one explicitly allowed agent operation.
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

        raise ValueError(
            f"Unsupported agent operation: {intent}"
        )

    @classmethod
    def _normalize_parameters(
        cls,
        parameters: dict[str, Any],
    ) -> dict:
        """
        Keep only explicitly supported parameters.
        """
        return {
            key: value
            for key, value in parameters.items()
            if key in cls.ALLOWED_PARAMETERS
        }

    @classmethod
    def _deterministic_fallback(
        cls,
        user_query: str,
    ) -> dict | None:
        """
        Narrow fallback for explicit, unambiguous commands.

        This parser only extracts information explicitly present in the
        user's request. It does not validate or execute financial actions.
        """

        normalized = " ".join(user_query.strip().split())

        # ------------------------------------------------------------
        # Refund payment
        #
        # Examples:
        #   Refund payment pay_ABC123
        #   Refund payment pay_ABC123 for ₹500
        #   Refund payment pay_ABC123 of 500
        # ------------------------------------------------------------

        refund_match = re.fullmatch(
            r"(?i)refund\s+(?:the\s+)?payment\s+"
            r"([A-Za-z0-9_]+)"
            r"(?:\s+(?:for|of)\s+(?:₹|rs\.?|inr)?\s*([\d,]+))?",
            normalized,
        )

        if refund_match:
            payment_id = refund_match.group(1)
            amount_text = refund_match.group(2)

            amount_in_paise = None

            if amount_text:
                amount_rupees = int(
                    amount_text.replace(",", "")
                )
                amount_in_paise = amount_rupees * 100

            return {
                "intent": "refund_payment",
                "parameters": {
                    "payment_id": payment_id,
                    "amount_in_paise": amount_in_paise,
                },
            }

        # ------------------------------------------------------------
        # Fetch payment
        #
        # Examples:
        #   Show payment pay_ABC123
        #   Fetch payment pay_ABC123
        #   Get payment pay_ABC123
        # ------------------------------------------------------------

        fetch_payment_match = re.fullmatch(
            r"(?i)(?:show|fetch|get)\s+"
            r"(?:the\s+)?payment\s+"
            r"([A-Za-z0-9_]+)",
            normalized,
        )

        if fetch_payment_match:
            return {
                "intent": "fetch_payment",
                "parameters": {
                    "payment_id": fetch_payment_match.group(1),
                },
            }

        # ------------------------------------------------------------
        # Fetch payment link
        #
        # Examples:
        #   Show payment link plink_ABC123
        #   Fetch payment link plink_ABC123
        # ------------------------------------------------------------

        fetch_link_match = re.fullmatch(
            r"(?i)(?:show|fetch|get)\s+"
            r"(?:the\s+)?payment\s+link\s+"
            r"([A-Za-z0-9_]+)",
            normalized,
        )

        if fetch_link_match:
            return {
                "intent": "fetch_payment_link",
                "parameters": {
                    "payment_link_id": fetch_link_match.group(1),
                },
            }

        # ------------------------------------------------------------
        # Create payment link
        #
        # Supported explicit forms:
        #
        #   Create a payment link for ₹500 for testing
        #   Create payment link for ₹500 for an invoice
        #   Create a ₹500 payment link for testing
        #
        # The fallback intentionally requires an explicit amount.
        # The description is taken only from explicitly supplied text.
        # ------------------------------------------------------------

        create_patterns = [
            re.fullmatch(
                r"(?i)create\s+(?:a\s+)?payment\s+link\s+"
                r"for\s+(?:₹|rs\.?|inr)?\s*([\d,]+)"
                r"(?:\s+for\s+(.+))?",
                normalized,
            ),
            re.fullmatch(
                r"(?i)create\s+(?:a\s+)?"
                r"(?:₹|rs\.?|inr)?\s*([\d,]+)"
                r"\s+payment\s+link"
                r"(?:\s+for\s+(.+))?",
                normalized,
            ),
        ]

        for create_match in create_patterns:
            if not create_match:
                continue

            amount_rupees = int(
                create_match.group(1).replace(",", "")
            )

            description = create_match.group(2)

            if description:
                description = description.strip()
            else:
                # Do not invent a description.
                description = None

            return {
                "intent": "create_payment_link",
                "parameters": {
                    "amount_in_paise": amount_rupees * 100,
                    "description": description,
                    "currency": "INR",
                },
            }

        return None

    @staticmethod
    def _parse_response(response: str) -> dict:
        """
        Parse the LLM's JSON response.

        Supports plain JSON and JSON wrapped in a Markdown code fence.
        """
        if not isinstance(response, str):
            raise ValueError(
                "Agent returned an invalid intent response."
            )

        cleaned = response.strip()

        if not cleaned:
            raise ValueError(
                "Agent returned an empty intent response."
            )

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].strip().startswith("```"):
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

    @staticmethod
    def _unsupported_route() -> dict:
        """
        Return the canonical representation for unsupported requests.
        """
        return {
            "intent": "unsupported",
            "parameters": {},
        }


agent_service = AgentService()