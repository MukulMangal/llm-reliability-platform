from app.models.ingestion import IngestionJob


class IngestionRepository:
    def __init__(self):
        self.jobs = []
        self.counter = 1

    def create(self, job: IngestionJob) -> IngestionJob:
        self.jobs.append(job)
        self.counter += 1
        return job

    def get_by_id(self, job_id: str) -> IngestionJob | None:
        for job in self.jobs:
            if job.id == job_id:
                return job

        return None


ingestion_repository = IngestionRepository()
