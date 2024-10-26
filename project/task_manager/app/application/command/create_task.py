import uuid
from dataclasses import dataclass
from sqlalchemy.exc import IntegrityError
from app.application.command.base import CommandProcessor
from app.common.message import Command
from pydantic import BaseModel

from app.domain.task import Task
from app.infrastrucrute.outbox.constants import OutboxEventTypes
from app.infrastrucrute.outbox.repositories import OutboxRepository
from app.infrastrucrute.repositories.task_repository import TaskRepository


class CreateTaskCommand(Command):
    task_id: uuid.UUID
    description: str
    creator_id: uuid.UUID
    assignee_id: uuid.UUID


class CreateTaskDTO(BaseModel):
    id: str


class DuplicateTaskError(Exception):
    pass


@dataclass
class CreateTaskCommandProcessor(CommandProcessor[CreateTaskCommand, CreateTaskDTO]):
    repository: TaskRepository
    outbox_repository: OutboxRepository

    async def process(self, command: CreateTaskCommand) -> CreateTaskDTO:
        task = Task.new(
            id=command.task_id,
            creator_id=command.creator_id,
            assignee_id=command.assignee_id,
            description=command.description,
        )
        async with self.repository.session() as session:
            await self.repository.add(task=task, session=session)

            for event in task.get_events():
                await self.outbox_repository.create_event(
                    event_type=OutboxEventTypes.task_assigned,
                    payload=event.model_dump_json(),
                    session=session,
                )
            try:
                await session.commit()
            except IntegrityError as exc:
                raise DuplicateTaskError(f"Task {task.id} already has") from exc

        return CreateTaskDTO(id=str(command.task_id))
