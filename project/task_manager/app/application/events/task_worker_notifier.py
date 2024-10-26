from dataclasses import asdict, dataclass

from app.common.domain.events import EventHandler
from app.domain.events import TaskAssignedDomainEvent
from app.infrastrucrute.gateways.email_notification import EmailNotificationGateway
from app.infrastrucrute.kafka.adapters.avro import KafkaAvroAdapter
from app.infrastrucrute.kafka.avro_models import TaskAssignedIntegrationEvent, TaskAssignedEventData, EventMeta
from app.infrastrucrute.kafka.client import KafkaTopicsEnum
from app.infrastrucrute.repositories.worker_repository import WorkerRepository


@dataclass
class NotifyWhenTaskAssignedEventHandler(EventHandler[TaskAssignedDomainEvent]):
    producer: KafkaAvroAdapter
    email_notification_gateway: EmailNotificationGateway
    worker_repository: WorkerRepository

    async def handle(self, event: TaskAssignedDomainEvent) -> None:

        worker = await self.worker_repository.get_worker_by_id(id=event.assignee_id)
        await self.email_notification_gateway.send_assigned_task(task_id=event.task_id, worker_email=worker.email)

        payload = TaskAssignedEventData(
            task_id=event.task_id, assignee_id=event.assignee_id, description=event.description
        )
        integration_event = TaskAssignedIntegrationEvent(
            meta=EventMeta(event_type=KafkaTopicsEnum.task_assigned), payload=payload
        )
        await self.producer.send(topic=KafkaTopicsEnum.task_assigned, record=asdict(integration_event))
