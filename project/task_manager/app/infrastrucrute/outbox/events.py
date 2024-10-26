from datetime import datetime
from pydantic import BaseModel

from app.common.message import Event


class OutboxEvent(BaseModel):
    outbox_id: int
    occurred_at: datetime
    data: Event