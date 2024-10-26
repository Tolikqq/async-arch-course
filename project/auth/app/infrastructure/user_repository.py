from dataclasses import dataclass
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.exceptions import UserNotFound
from app.database import Database
from app.infrastructure.orm import UserORM, RoleEnum
from sqlalchemy.exc import NoResultFound


@dataclass
class UserRepository:
    db: Database

    async def create_user(self, username: str, password: str) -> UserORM:
        async with self.db.session() as session:
            user = UserORM(email=username, role=RoleEnum.worker.value, password_hash=password)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

    async def get_by_email(self, email: EmailStr) -> UserORM | None:
        query = select(UserORM).where(UserORM.email == email)

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_by_id(self, public_id: str) -> UserORM:
        query = select(UserORM).where(UserORM.public_id == public_id)
        async with (self.db.session() as session):
            try:
                result = await session.execute(query)
                return result.scalar_one()
            except NoResultFound as exc:
                raise UserNotFound from exc

