from uuid import UUID, uuid4
from dataclasses import dataclass, field
from datetime import datetime
from dataclasses_avroschema import AvroModel

from app.common.constants import MOSCOW_TZ

EVENT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


@dataclass
class EventMeta(AvroModel):
    event_type: str
    event_created_at: datetime = field(default_factory=lambda: datetime.now(tz=MOSCOW_TZ))
    event_id: UUID = field(default_factory=uuid4)


@dataclass
class TaskCompletedEventData(AvroModel):
    task_id: UUID


@dataclass
class TaskCompletedIntegrationEvent(AvroModel):
    meta: EventMeta
    payload: TaskCompletedEventData


@dataclass
class TaskAssignedEventData(AvroModel):
    task_id: UUID
    assignee_id: UUID
    description: str


@dataclass
class TaskAssignedIntegrationEvent(AvroModel):
    meta: EventMeta
    payload: TaskAssignedEventData
