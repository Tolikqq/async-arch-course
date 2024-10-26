from uuid import UUID

from app.common.message import Event


class TaskAssignedDomainEvent(Event):
    task_id: UUID
    assignee_id: UUID
    description: str


class TaskCompletedDomainEvent(Event):
    task_id: UUID
