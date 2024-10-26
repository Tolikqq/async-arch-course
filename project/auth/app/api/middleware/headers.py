from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.ctx_vars import generate_request_id, set_ctx_request_id, _request_id_ctx

REQUEST_ID_HEADER_NAME = "Request-Id"


class HeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request_headers = Headers(scope=scope)
        request_id = request_headers.get(REQUEST_ID_HEADER_NAME, generate_request_id())
        set_ctx_request_id(request_id)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                response_headers[REQUEST_ID_HEADER_NAME] = request_id
            await send(message)

        await self.app(scope, receive, send_wrapper)
