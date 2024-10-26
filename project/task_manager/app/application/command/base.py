from typing import Generic, TypeVar

T = TypeVar('T')
E = TypeVar('E')


class CommandProcessor(Generic[T, E]):

    async def process(self, command: T) -> E:
        raise NotImplementedError

