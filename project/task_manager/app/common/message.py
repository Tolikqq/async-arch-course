from pydantic import BaseModel


class Command(BaseModel):
    """Base class for all commands"""


class Event(BaseModel):
    """Base class for all events"""


