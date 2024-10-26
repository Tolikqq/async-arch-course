from dataclasses import dataclass

from app.application.events.task_worker_notifier import NotifyWhenTaskAssignedEventHandler
from app.common.message import Event
from app.domain.events import TaskAssignedDomainEvent


@dataclass
class OutboxEventDispatcher:
    task_assigned_event_handler: NotifyWhenTaskAssignedEventHandler

    async def handle(self, event: Event) -> None:
        if isinstance(event, TaskAssignedDomainEvent):
            await self.task_assigned_event_handler.handle(event)
        else:
            raise ValueError(f"No handler found for event type: {type(event).__name__}")