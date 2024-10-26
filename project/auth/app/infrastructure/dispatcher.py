from datetime import datetime
import uuid
import pytz
from typing import cast
from dataclasses import dataclass, asdict
from app.application.events import Event, UserCreated
from app.ctx_vars import get_ctx_request_id
from app.infrastructure.avro_models import UserCreatedEvent, EventMeta, UserCreatedEventData
from settings.kafka.adapters.avro import KafkaAvroAdapter
from settings.kafka.client import KafkaTopicsEnum


@dataclass
class UserEventDispatcher:
    producer: KafkaAvroAdapter

    async def handle(self, event: Event) -> None:
        match event:
            case UserCreated():
                event = cast(UserCreated, event)
                meta = EventMeta(event_created_at=datetime.now(tz=pytz.timezone("Europe/Moscow")),
                                 event_id=uuid.uuid4(),
                                 event_type="user_created",
                                 )
                payload = UserCreatedEventData(public_id=event.public_id, email=event.email, role=event.role)
                record = UserCreatedEvent(meta=meta, payload=payload)
                await self.producer.send(topic=KafkaTopicsEnum.user_stream,
                                         record=asdict(record),
                                         headers={"request_id": get_ctx_request_id()}
                                         )
            case _:
                raise ValueError(f"Unexpected event {event}")
