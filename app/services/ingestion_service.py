from datetime import datetime, timezone

from app.models.ingestion import IngestionJob
from app.repositories.ingestion_repository import ingestion_repository


class IngestionService:
    def create(self, document_id: str) -> IngestionJob:
        job = IngestionJob(
            id=f"job_{ingestion_repository.counter:03}",
            document_id=document_id,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )

        return ingestion_repository.create(job)

    def get_by_id(self, job_id: str) -> IngestionJob | None:
        return ingestion_repository.get_by_id(job_id)


ingestion_service = IngestionService()