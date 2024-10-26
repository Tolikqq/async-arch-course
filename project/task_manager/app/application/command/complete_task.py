from uuid import UUID
from dataclasses import dataclass

from app.application.command.base import CommandProcessor
from app.common.message import Command

from app.infrastrucrute.repositories.task_repository import TaskRepository
from app.infrastrucrute.task_dispatcher import TaskEventDispatcher


class CompleteTaskCommand(Command):
    task_id: UUID
    worker_id: UUID


@dataclass
class CompleteTaskCommandProcessor(CommandProcessor[CompleteTaskCommand, None]):
    repository: TaskRepository
    event_dispatcher: TaskEventDispatcher

    async def process(self, command: CompleteTaskCommand) -> None:

        task = await self.repository.get_assigned_task(task_id=command.task_id, worker_id=command.worker_id)
        task.complete()

        async with self.repository.session() as session:
            await self.repository.update(task=task, session=session)
            await session.commit()

        await self.event_dispatcher.handle(events=task.get_events())

