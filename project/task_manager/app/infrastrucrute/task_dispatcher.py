from dataclasses import dataclass, asdict

from app.common.message import Event

from app.domain.events import TaskCompletedDomainEvent

from app.infrastrucrute.kafka.adapters.avro import KafkaAvroAdapter
from app.infrastrucrute.kafka.avro_models import TaskCompletedEventData, EventMeta, TaskCompletedIntegrationEvent
from app.infrastrucrute.kafka.client import KafkaTopicsEnum


@dataclass
class TaskEventDispatcher:
    producer: KafkaAvroAdapter

    async def handle(self, events: list[Event]) -> None:
        for event in events:
            await self._handle(event)

    async def _handle(self, event: Event) -> None:
        match event:
            case TaskCompletedDomainEvent():
                integration_event = TaskCompletedIntegrationEvent(
                    meta=EventMeta(event_type=KafkaTopicsEnum.task_completed),
                    payload=TaskCompletedEventData(task_id=event.task_id)
                )
                await self.producer.send(topic=KafkaTopicsEnum.task_completed, record=asdict(integration_event))
            case _:
                raise ValueError(f"Unexpected event {event}")
