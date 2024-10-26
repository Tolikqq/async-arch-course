from typing import Annotated

from fastapi import Depends, HTTPException, Request, Query
from fastapi.security import OAuth2PasswordBearer
from starlette import status
import jwt

from dependency_injector.wiring import Provide, inject

from app.application.worker_service import WorkerService
from app.common.domain.exceptions import EntityNotFoundException
from app.common.pagination import OffsetPagination
from app.domain.worker import Worker
from app.infrastrucrute.di.container import DIContainer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


@inject
async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        worker_service: WorkerService = Depends(Provide[DIContainer.services.worker_service])
) -> Worker:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid: str = payload.get("public_id")
        if user_uuid is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    try:
        worker = await worker_service.get_worker_by_id(public_id=user_uuid)
    except EntityNotFoundException as ex:
        raise credentials_exception from ex
    return worker


async def get_offset_pagination(
    request: Request,
    offset: int = Query(default=0, ge=0, description="Пропустить первые в выдаче N объектов до этого значения"),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Верхний лимит объектов в выдаче, максимальное значение 100",
    ),
) -> OffsetPagination:
    """Дефолтная офсетная пагинация."""
    return OffsetPagination(limit=limit, offset=offset, request_url=request.url)