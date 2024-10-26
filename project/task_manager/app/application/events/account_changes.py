from dataclasses import dataclass
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.common.message import Event
from app.domain.worker import Worker, Role
from app.infrastrucrute.repositories.worker_repository import WorkerRepository


class EventMeta(BaseModel):
    event_id: uuid.UUID
    event_type: str
    event_created_at: datetime


class AccountChangesData(BaseModel):
    public_id: uuid.UUID
    email: str
    role: Role


class AccountChangesEvent(Event):
    meta: EventMeta
    payload: AccountChangesData


@dataclass
class AccountChangesEventHandler:
    repository: WorkerRepository

    async def execute(self, record: dict[str, Any]) -> None:
        event = AccountChangesEvent.model_validate(record)
        if event.meta.event_type == "user_created":
            await self._create_worker(event=event)

    async def _create_worker(self, event: AccountChangesEvent) -> None:
        worker = Worker.new(id=event.payload.public_id, email=event.payload.email, role=event.payload.role)
        async with self.repository.session() as session:
            await self.repository.add(worker=worker, session=session)
            await session.commit()
