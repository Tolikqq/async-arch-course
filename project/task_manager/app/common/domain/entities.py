from dataclasses import dataclass, field
from app.common.message import Event


@dataclass(kw_only=True)
class AggregateRoot:

    _events: list[Event] = field(default_factory=list)

    def add_event(self, *event: Event) -> None:
        if not event:
            self._events = []
        self._events.extend(event)

    def get_events(self) -> list[Event]:
        if not self._events:
            self._events = []
        events = self._events.copy()
        self._events.clear()
        return events
