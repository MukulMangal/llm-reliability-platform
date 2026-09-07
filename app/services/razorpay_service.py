import httpx

from app.core.config import settings


class RazorpayService:
    """
    Client for interacting with the Razorpay API in Test Mode.

    This service is responsible only for communicating with Razorpay.
    Business validation and financial safety rules remain in the
    agent/tool layer.
    """

    def __init__(self) -> None:
        self.base_url = settings.RAZORPAY_BASE_URL.rstrip("/")
        self.auth = (
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )

    def get(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict:
        return self._request(
            "GET",
            endpoint,
            params=params,
        )

    def post(
        self,
        endpoint: str,
        data: dict | None = None,
    ) -> dict:
        return self._request(
            "POST",
            endpoint,
            data=data,
        )

    def create_payment_link(
        self,
        amount: int,
        description: str,
        currency: str = "INR",
    ) -> dict:
        if amount <= 0:
            raise ValueError(
                "Payment link amount must be greater than zero."
            )

        if not description.strip():
            raise ValueError(
                "Payment link description cannot be empty."
            )

        payload = {
            "amount": amount,
            "currency": currency.upper(),
            "description": description,
        }

        return self.post(
            "/payment_links",
            payload,
        )

    def fetch_payment_link(
        self,
        payment_link_id: str,
    ) -> dict:
        if not payment_link_id.strip():
            raise ValueError(
                "Payment link ID cannot be empty."
            )

        return self.get(
            f"/payment_links/{payment_link_id}"
        )

    def fetch_payment(
        self,
        payment_id: str,
    ) -> dict:
        if not payment_id.strip():
            raise ValueError(
                "Payment ID cannot be empty."
            )

        return self.get(
            f"/payments/{payment_id}"
        )

    def list_payments(
        self,
        count: int = 20,
        skip: int = 0,
    ) -> dict:
        return self.get(
            "/payments",
            params={
                "count": count,
                "skip": skip,
            },
        )

    def list_payment_links(
        self,
        count: int = 20,
        skip: int = 0,
    ) -> dict:
        return self.get(
            "/payment_links",
            params={
                "count": count,
                "skip": skip,
            },
        )

    def list_refunds(
        self,
        count: int = 20,
        skip: int = 0,
    ) -> dict:
        return self.get(
            "/refunds",
            params={
                "count": count,
                "skip": skip,
            },
        )

    def refund_payment(
        self,
        payment_id: str,
        amount: int | None = None,
    ) -> dict:
        if not payment_id.strip():
            raise ValueError(
                "Payment ID cannot be empty."
            )

        if amount is not None and amount <= 0:
            raise ValueError(
                "Refund amount must be greater than zero."
            )

        payload = {}

        if amount is not None:
            payload["amount"] = amount

        return self.post(
            f"/payments/{payment_id}/refund",
            payload,
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """
        Execute a Razorpay API request with authentication.

        Razorpay API error descriptions are preserved in a safe,
        user-readable RuntimeError so the agent can distinguish
        validation/business failures from generic connectivity errors.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = httpx.request(
                method=method,
                url=url,
                auth=self.auth,
                json=data,
                params=params,
                timeout=10.0,
            )

            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as exc:
            error_message = self._extract_api_error(exc.response)

            raise RuntimeError(
                error_message
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Unable to connect to Razorpay API"
            ) from exc

    @staticmethod
    def _extract_api_error(response: httpx.Response) -> str:
        """
        Extract Razorpay's safe error description from an HTTP response.

        Razorpay commonly returns:
        {
            "error": {
                "code": "...",
                "description": "..."
            }
        }

        If the response cannot be parsed, fall back to the HTTP status.
        """
        try:
            payload = response.json()
        except ValueError:
            payload = None

        if isinstance(payload, dict):
            error = payload.get("error")

            if isinstance(error, dict):
                description = error.get("description")

                if isinstance(description, str) and description.strip():
                    return description.strip()

        return (
            "Razorpay API request failed with status "
            f"{response.status_code}"
        )


razorpay_service = RazorpayService()