from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from app.application.exceptions import InvalidCredentialsException, UserAlreadyExists
from app.infrastructure.orm import UserORM
from app.infrastructure.user_repository import UserRepository
from app.application.events import UserCreated
from app.infrastructure.dispatcher import UserEventDispatcher

ACCESS_TOKEN_EXPIRE_MINUTES = 300
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class UserService:
    repository: UserRepository
    event_dispatcher: UserEventDispatcher

    async def register_user(self, email: str, password: str) -> UserORM:
        db_user = await self.repository.get_by_email(email=email)
        if db_user:
            raise UserAlreadyExists
        user = await self.repository.create_user(email, self.hashed_password(password))

        await self.event_dispatcher.handle(event=UserCreated(public_id=user.public_id, role=user.role, email=user.email))
        return user

    async def authenticate_with_name_and_password(self, email: str, password: str) -> str:
        user = await self.repository.get_by_email(email=email)
        if not user:
            raise InvalidCredentialsException

        if not self.verify_password(password, user.password_hash):
            raise InvalidCredentialsException

        return self.create_access_token(data={"public_id": user.public_id.hex})

    async def get_user_by_id(self, public_id: str) -> UserORM:
        return await self.repository.get_by_id(public_id=public_id)

    @staticmethod
    def create_access_token(data: dict) -> str:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hashed_password(password):
        return pwd_context.hash(password)


