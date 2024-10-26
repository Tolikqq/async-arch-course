import uuid
from dataclasses import dataclass
from datetime import datetime
from dataclasses_avroschema import AvroModel

EVENT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


@dataclass
class EventMeta(AvroModel):
    event_id: uuid.UUID
    event_type: str
    event_created_at: datetime


@dataclass
class UserCreatedEventData(AvroModel):
    public_id: uuid.UUID
    email: str
    role: str


@dataclass
class UserCreatedEvent(AvroModel):
    meta: EventMeta
    payload: UserCreatedEventData
