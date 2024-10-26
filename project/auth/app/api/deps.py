from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
import jwt
from app.application.services import SECRET_KEY, ALGORITHM, UserService
from dependency_injector.wiring import Provide, inject

from app.infrastructure.orm import UserORM
from application.exceptions import UserNotFound
from settings.di.container import DIContainer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@inject
async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        user_service: UserService = Depends(Provide[DIContainer.services.user_service])
) -> UserORM:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid: str = payload.get("public_id")
        if user_uuid is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    try:
        user = await user_service.get_user_by_id(public_id=user_uuid)
    except UserNotFound as ex:
        raise credentials_exception from ex
    return user
