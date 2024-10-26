from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from dependency_injector.wiring import Provide, inject

from app.api.deps import get_current_user
from app.application.exceptions import InvalidCredentialsException, UserAlreadyExists
from app.application.services import UserService
from app.infrastructure.orm import UserORM
from app.ctx_vars import get_ctx_request_id, _request_id_ctx
from settings.di.container import DIContainer

router = APIRouter()


class UserResponse(BaseModel):
    id: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: str
    password: str


@router.post("/token")
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(Provide[DIContainer.services.user_service])
) -> LoginResponse:
    try:
        access_token = await user_service.authenticate_with_name_and_password(
            form_data.username, form_data.password
        )
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    return LoginResponse(access_token=access_token, token_type="bearer")


@router.post("/users/")
@inject
async def create_user(
        user: UserCreate,
        user_service: UserService = Depends(Provide[DIContainer.services.user_service])
) -> UserResponse:
    try:
        new_user = await user_service.register_user(email=user.email, password=user.password)
    except UserAlreadyExists:
        raise HTTPException(status_code=400, detail="Email already registered")
    return UserResponse(id=str(new_user.public_id))


@router.get("/users/me")
async def get_users_me(
        current_user: Annotated[UserORM, Depends(get_current_user)],
) -> UserResponse:

    return UserResponse(id=str(current_user.public_id))