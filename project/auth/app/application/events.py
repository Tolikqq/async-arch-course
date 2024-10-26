from dataclasses import dataclass
from uuid import UUID


class Event:
    ...


@dataclass
class UserCreated(Event):
    public_id: UUID
    email: str
    role: str
