from contextvars import ContextVar, Token
from uuid import uuid4

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def generate_request_id() -> str:
    return uuid4().hex


def get_ctx_request_id() -> str | None:
    return _request_id_ctx.get()


def set_ctx_request_id(request_id: str) -> Token[str | None]:
    return _request_id_ctx.set(request_id)
