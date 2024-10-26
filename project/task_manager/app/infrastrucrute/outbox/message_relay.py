from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
from loguru import logger
import orjson
from app.common.message import Event
from app.domain.events import TaskAssignedDomainEvent
from app.infrastrucrute.outbox.constants import OutboxEventTypes
from app.infrastrucrute.outbox.event_dispather import OutboxEventDispatcher
from app.infrastrucrute.outbox.events import OutboxEvent
from app.infrastrucrute.outbox.models import Outbox
from app.infrastrucrute.outbox.repositories import OutboxRepository


@dataclass
class OutboxProcessor:
    outbox_repository: OutboxRepository
    event_dispatcher: OutboxEventDispatcher

    async def run(self) -> None:
        while True:
            events = await self._get_unhandled_events()
            for event in events:
                await self.event_dispatcher.handle(event=event.data)
                await self._set_events_processed(outbox_ids=[event.outbox_id])

    async def _get_unhandled_events(self) -> list[OutboxEvent]:
        event_types = [event_type for event_type in list(OutboxEventTypes)]
        records = await self.outbox_repository.get_unhandled_events(event_types=event_types)
        events = []
        wrong_events_ids = []

        for record in records:
            try:
                events.append(OutboxRecordToEventTranslator.translate(record))
            except OutboxTranslatorValidationError as error:
                logger.exception("outbox payload format must be json", error=repr(error), outbox_id=record.id)
                wrong_events_ids.append(record.id)

        if wrong_events_ids:
            # помечаем processed_at, но не отправляем некорректные данные
            await self._set_events_processed(wrong_events_ids)

        return events

    async def _set_events_processed(self, outbox_ids: list[int]) -> None:
        await self.outbox_repository.update_events_processed(outbox_ids=outbox_ids)


@dataclass
class OutboxRecordToEventTranslator:
    _mapper: ClassVar[dict] = {  # type: ignore[type-arg]
        OutboxEventTypes.task_assigned: TaskAssignedDomainEvent,
    }

    @classmethod
    def translate(cls, record: Outbox) -> OutboxEvent:
        try:
            event_class = cls._mapper[record.event_type]
            data = orjson.loads(record.payload)
            return OutboxEvent(
                outbox_id=record.id,
                occurred_at=record.occurred_at,
                data=event_class.model_validate(data)
            )
        except Exception as error:
            raise OutboxTranslatorValidationError from error


class OutboxTranslatorValidationError(Exception):
    pass
