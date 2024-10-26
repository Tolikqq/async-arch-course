from dataclasses import dataclass
from uuid import UUID

from app.domain.worker import Worker
from app.infrastrucrute.repositories.worker_repository import WorkerRepository


@dataclass
class WorkerService:
    repository: WorkerRepository

    async def get_worker_by_id(self, public_id: str) -> Worker:
        return await self.repository.get_worker_by_id(id=UUID(public_id))
