from abc import abstractmethod, ABC
from typing import Any, Iterable

import orjson


class KafkaEncoder(ABC):
    @abstractmethod
    async def encode_message(self, record: dict[str, Any], topic: str) -> bytes: ...

    @abstractmethod
    async def encode_key(self, key: dict[str, int] | None, topic: str) -> bytes | None: ...

    async def encode_headers(self, headers: dict[str, Any] | None) -> Iterable[tuple[str, bytes]] | None:
        if headers is None:
            return None
        return [(key, orjson.dumps(value)) for key, value in headers.items()]