from typing import Generic, TypeVar

TQuery = TypeVar('TQuery')
TResult = TypeVar('TResult')


class QueryHandler(Generic[TQuery, TResult]):

    async def handle(self, query: TQuery) -> TResult:
        raise NotImplementedError

