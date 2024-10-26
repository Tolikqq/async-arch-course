import enum
from dataclasses import dataclass
from uuid import UUID

from app.common.domain.entities import AggregateRoot
from app.domain.events import TaskAssignedDomainEvent, TaskCompletedDomainEvent


class StatusEnum(enum.StrEnum):
    open = "open"
    done = "done"


class TaskNotOpenError(Exception):
    pass


@dataclass
class Task(AggregateRoot):
    id: UUID
    description: str
    status: StatusEnum

    assignee_id: UUID
    creator_id: UUID

    @classmethod
    def new(cls, id: UUID, description: str, creator_id: UUID, assignee_id: UUID) -> "Task":
        task = Task(
            id=id,
            description=description,
            status=StatusEnum.open,
            assignee_id=assignee_id,
            creator_id=creator_id
        )
        task.add_event(TaskAssignedDomainEvent(
            task_id=task.id, assignee_id=task.assignee_id, description=task.description)
        )
        return task

    def assign(self, worker_id: UUID) -> None:
        self.assignee_id = worker_id
        self.add_event(TaskAssignedDomainEvent(
            task_id=self.id, assignee_id=self.assignee_id, description=self.description)
        )

    def complete(self) -> None:
        if self.status != StatusEnum.open:
            raise TaskNotOpenError("Task status is not open")
        self.status = StatusEnum.done

        self.add_event(TaskCompletedDomainEvent(task_id=self.id))
