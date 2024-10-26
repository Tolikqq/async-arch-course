from dataclasses import dataclass

from sqlalchemy import func, null, select, update
from sqlalchemy.dialects.mysql import insert

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import DBSessionFactory
from app.infrastrucrute.outbox.constants import NOTIFICATIONS_OUTBOX_LIMIT
from app.infrastrucrute.outbox.models import Outbox


@dataclass
class OutboxRepository:
    session: DBSessionFactory

    async def get_unhandled_events(self, event_types: list[str]) -> list[Outbox]:
        query = (
            select(Outbox)
            .where(
                Outbox.event_type.in_(event_types),
                Outbox.processed_at == null(),
            )
            .order_by(Outbox.occurred_at)
            .limit(NOTIFICATIONS_OUTBOX_LIMIT)
        )
        async with self.session() as session:
            result = await session.execute(query)
            return list(result.scalars().all())

    async def create_event(
        self,
        event_type: str,
        payload: str,
        session: AsyncSession | None = None,
    ) -> None:
        insert_query = insert(Outbox).values(
            {
                Outbox.event_type: event_type,
                Outbox.payload: payload,
            }
        )
        if session is not None:
            await session.execute(insert_query)
        else:
            async with self.session() as session:
                await session.execute(insert_query)
                await session.commit()

    async def update_events_processed(self, outbox_ids: list[int]) -> None:
        update_query = update(Outbox).where(Outbox.id.in_(outbox_ids)).values(processed_at=func.now())
        async with self.session() as session:
            await session.execute(update_query)
            await session.commit()
