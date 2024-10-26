from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from pydantic import BaseModel

from app.application.query.base import QueryHandler
from app.database import Database
from app.infrastrucrute.orm import TaskORM
from app.domain.task import StatusEnum


class GetTasksListQuery(BaseModel):
    assignee_id: UUID


class TaskDTO(BaseModel):
    id: UUID
    status: StatusEnum
    description: str


@dataclass
class GetTasksQueryHandler(QueryHandler[GetTasksListQuery, list[TaskDTO]]):
    db: Database

    async def handle(self, query: GetTasksListQuery) -> list[TaskDTO]:
        async with self.db.session() as session:
            stmt = select(TaskORM).where(
                TaskORM.assignee_id == query.assignee_id
            )
            result = await session.execute(stmt)
            tasks = result.scalars().all()
            return [TaskDTO(id=task.id, status=task.status, description=task.description) for task in tasks]


