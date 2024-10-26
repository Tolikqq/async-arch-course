from typing import Generic, TypeVar

TEvent = TypeVar('TEvent')


class DomainEvent:
    pass


class EventHandler(Generic[TEvent]):

    async def handle(self, event: TEvent) -> None:
        raise NotImplementedError
