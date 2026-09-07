from datetime import datetime, timezone
from threading import Lock


class ActivityService:
    """
    In-memory activity and audit service for the payment operations agent.

    Each record captures the high-level outcome of an agent operation without
    storing secrets or raw internal exceptions.

    This is intentionally lightweight for the MVP. The service can later be
    replaced by a persistent repository without changing the agent API.
    """

    MAX_RECORDS = 100

    def __init__(self) -> None:
        self._records: list[dict] = []
        self._lock = Lock()

    def record(
        self,
        *,
        user_query: str,
        operation: str,
        status: str,
        success: bool,
        message: str | None = None,
        reliability: dict | None = None,
        result: dict | None = None,
    ) -> dict:
        """
        Record a normalized agent activity event.

        Sensitive authentication information is never recorded. The Razorpay
        result is reduced to safe operational metadata where possible.
        """
        record = {
            "id": self._create_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_query": user_query,
            "operation": operation,
            "status": status,
            "success": success,
            "message": message,
            "reliability_score": self._reliability_score(reliability),
            "result_summary": self._summarize_result(result),
        }

        with self._lock:
            self._records.insert(0, record)
            del self._records[self.MAX_RECORDS :]

        return record

    def list_recent(self, limit: int = 20) -> list[dict]:
        """
        Return the most recent activity records.
        """
        if limit < 1:
            return []

        with self._lock:
            return list(self._records[:limit])

    def clear(self) -> None:
        """
        Clear activity records.

        Primarily useful for development and testing.
        """
        with self._lock:
            self._records.clear()

    @staticmethod
    def _create_id() -> str:
        """
        Generate a short unique activity identifier.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        return f"act_{timestamp}"

    @staticmethod
    def _reliability_score(
        reliability: dict | None,
    ) -> float | None:
        """
        Extract and normalize the reliability score.
        """
        if not reliability:
            return None

        score = reliability.get("reliability_score")

        if not isinstance(score, (int, float)):
            return None

        return round(max(0.0, min(1.0, float(score))), 2)

    @staticmethod
    def _summarize_result(
        result: dict | None,
    ) -> dict | None:
        """
        Store only useful operational metadata from an API result.

        Full Razorpay responses are intentionally not persisted in the
        activity log.
        """
        if not isinstance(result, dict):
            return None

        summary = {}

        for key in (
            "id",
            "status",
            "amount",
            "currency",
            "description",
            "short_url",
        ):
            if key in result:
                summary[key] = result[key]

        return summary or None


activity_service = ActivityService()