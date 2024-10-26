from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session, AsyncSession


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, url: str, debug: bool):
        self.engine = create_async_engine(url=url, echo=debug)
        self._async_session = async_scoped_session(
            session_factory=async_sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False
            ),
            scopefunc=current_task,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._async_session()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
