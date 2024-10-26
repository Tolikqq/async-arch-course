import uuid
from dataclasses import dataclass
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.exceptions import EntityNotFoundException
from app.database import DBSessionFactory
from app.domain.worker import Worker
from app.infrastrucrute.orm import WorkerORM, ASSIGNABLE_ROLES


@dataclass
class WorkerRepository:
    session: DBSessionFactory

    async def add(self, worker: Worker, session: AsyncSession) -> None:
        worker_orm = WorkerORM.from_domain(worker)
        session.add(worker_orm)

    async def get_worker_by_id(self, id: uuid.UUID) -> Worker:
        query = select(WorkerORM).where(WorkerORM.id == id)
        async with self.session() as session:
            result = await session.execute(query)
            try:
                worker = result.scalar_one()
                return worker.to_domain()
            except NoResultFound as exc:
                raise EntityNotFoundException(identifier=id) from exc

    async def get_assignable_workers(self) -> list[Worker]:
        query = select(WorkerORM).where(WorkerORM.role.in_(ASSIGNABLE_ROLES))
        async with self.session() as session:
            result = await session.execute(query)
            workers = result.scalars().all()
            return [worker.to_domain() for worker in workers]

