from uuid import UUID
from dataclasses import dataclass
import random

from app.application.command.base import CommandProcessor
from app.common.message import Command


from app.domain.task import Task
from app.domain.worker import Worker
from app.infrastrucrute.outbox.constants import OutboxEventTypes
from app.infrastrucrute.outbox.repositories import OutboxRepository
from app.infrastrucrute.repositories.task_repository import TaskRepository
from app.infrastrucrute.repositories.worker_repository import WorkerRepository


class ReassignTasksCommand(Command):
    worker_id: UUID


class UserDoesNotHavePermission(Exception):
    pass


@dataclass
class ReassignTasksCommandProcessor(CommandProcessor[ReassignTasksCommand, None]):
    repository: TaskRepository
    worker_repository: WorkerRepository
    outbox_repository: OutboxRepository

    async def process(self, command: ReassignTasksCommand) -> None:

        await self._validate_worker_permission(worker_id=command.worker_id)

        tasks = await self.repository.get_all_open_tasks()
        workers = await self.worker_repository.get_assignable_workers()

        TaskAssigner.reassign_tasks(workers=workers, tasks=tasks)

        async with self.repository.session() as session:
            for task in tasks:
                await self.repository.update(task=task, session=session)
                for event in task.get_events():
                    await self.outbox_repository.create_event(
                        event_type=OutboxEventTypes.task_assigned,
                        payload=event.model_dump_json(),
                        session=session,
                    )
            await session.commit()

    async def _validate_worker_permission(self, worker_id: UUID) -> None:
        worker = await self.worker_repository.get_worker_by_id(id=worker_id)
        if not worker.is_admin_role:
            raise UserDoesNotHavePermission


class TaskAssigner:

    @staticmethod
    def reassign_tasks(workers: list[Worker], tasks: list[Task]) -> None:
        for task in tasks:
            worker = random.choice(workers)
            task.assign(worker_id=worker.id)