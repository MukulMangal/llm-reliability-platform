import httpx

from app.core.config import settings


class RazorpayService:
    """
    Client for interacting with the Razorpay API in Test Mode.
    """

    def __init__(self) -> None:
        self.base_url = settings.RAZORPAY_BASE_URL.rstrip("/")
        self.auth = (
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )

    def get(self, endpoint: str) -> dict:
        """
        Send a GET request to the Razorpay API.
        """
        return self._request("GET", endpoint)

    def post(self, endpoint: str, data: dict) -> dict:
        """
        Send a POST request to the Razorpay API.
        """
        return self._request("POST", endpoint, data=data)

    def create_payment_link(
        self,
        amount: int,
        description: str,
        currency: str = "INR",
    ) -> dict:
        """
        Create a Razorpay Payment Link.

        Amount must be provided in the smallest currency unit.
        For INR, 10000 represents ₹100.00.
        """
        if amount <= 0:
            raise ValueError("Payment link amount must be greater than zero.")

        if not description.strip():
            raise ValueError("Payment link description cannot be empty.")

        payload = {
            "amount": amount,
            "currency": currency,
            "description": description,
        }

        return self.post("/payment_links", payload)

    def fetch_payment_link(self, payment_link_id: str) -> dict:
        """
        Fetch a Razorpay Payment Link by ID.
        """
        if not payment_link_id.strip():
            raise ValueError("Payment link ID cannot be empty.")

        return self.get(f"/payment_links/{payment_link_id}")

    def fetch_payment(self, payment_id: str) -> dict:
        """
        Fetch a Razorpay Payment by ID.
        """
        if not payment_id.strip():
            raise ValueError("Payment ID cannot be empty.")

        return self.get(f"/payments/{payment_id}")

    def refund_payment(
        self,
        payment_id: str,
        amount: int | None = None,
    ) -> dict:
        """
        Refund a Razorpay payment.

        If amount is omitted, Razorpay processes a full refund.
        Amount must be provided in the smallest currency unit.
        """
        if not payment_id.strip():
            raise ValueError("Payment ID cannot be empty.")

        if amount is not None and amount <= 0:
            raise ValueError("Refund amount must be greater than zero.")

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
    ) -> dict:
        """
        Execute a Razorpay API request with authentication and
        consistent error handling.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = httpx.request(
                method=method,
                url=url,
                auth=self.auth,
                json=data,
                timeout=10.0,
            )

            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Razorpay API request failed with status "
                f"{exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Unable to connect to Razorpay API"
            ) from exc


razorpay_service = RazorpayService()