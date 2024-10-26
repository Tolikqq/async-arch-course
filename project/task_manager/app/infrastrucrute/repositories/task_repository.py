from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass
from sqlalchemy import select

from app.common.domain.exceptions import EntityNotFoundException
from app.database import DBSessionFactory
from app.domain.task import Task, StatusEnum
from app.infrastrucrute.orm import TaskORM


@dataclass
class TaskRepository:
    session: DBSessionFactory

    async def add(self, task: Task, session: AsyncSession) -> None:
        task_orm =TaskORM.from_domain(task)
        session.add(task_orm)

    async def update(self, task: Task, session: AsyncSession) -> None:
        task_orm =TaskORM.from_domain(task)
        await session.merge(task_orm)

    async def get_all_open_tasks(self) -> list[Task]:
        query = select(TaskORM).where(TaskORM.status == StatusEnum.open)
        async with self.session() as session:
            result = await session.execute(query)
            tasks = result.scalars().all()
            return [task.to_domain() for task in tasks]

    async def get_assigned_task(self, task_id: UUID, worker_id: UUID) -> Task:
        task = await self.get_task_by_id(task_id=task_id)
        if task.assignee_id != worker_id:
            raise EntityNotFoundException(identifier=task_id)
        return task

    async def get_task_by_id(self, task_id: UUID) -> Task:
        query = select(TaskORM).where(TaskORM.id == task_id)
        async with self.session() as session:
            result = await session.execute(query)
            task = result.one_or_none()

        if not task:
            raise EntityNotFoundException(identifier=task_id)

        return task.to_domain()
