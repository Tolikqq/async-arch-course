import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvloop
from fastapi import FastAPI, Depends
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from aiokafka import AIOKafkaProducer

from app.infrastrucrute.di.apaters import initialize_kafka_client
from app.infrastrucrute.kafka.client import KafkaClient

class AsyncProvide(Provide):
    async def __call__(self):
        return self

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class Service:
    def __init__(self, resource):
        self.resource = resource

    async def process(self) -> str:
        assert asyncio.get_running_loop() is self.resource.producer._loop
        print("OK")

def create_kafka_client() -> KafkaClient:
    return KafkaClient(producer=AIOKafkaProducer(bootstrap_servers="localhost:9092"))

class Container(containers.DeclarativeContainer):
    kafka_client_ = providers.Singleton(create_kafka_client)
    kafka_client = providers.Resource(initialize_kafka_client, kafka_client_, )
    service = providers.Singleton(Service, resource=kafka_client)

# class KafkaConsumerApp:
#     def __init__(self) -> None:
#         self.container = self.create_di_container()
#
#     def create_di_container(self) -> Container:
#         container = Container()
#         container.wire(packages=[__name__])
#         return container
#
#     async def run(self) -> None:
#         await self.container.init_resources()  # type: ignore[misc]
#         try:
#             service = await self.container.service()
#             await service.process()
#         finally:
#             shutdown_coro = self.container.shutdown_resources()
#             if shutdown_coro:
#                 await shutdown_coro



# if __name__ == "__main__":
#     consumer = KafkaConsumerApp()
#     uvloop.install()
#     asyncio.run(consumer.run())

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await container.init_resources()
    yield
    await container.shutdown_resources()

app = FastAPI(lifespan=lifespan)




@app.api_route("/")
@inject
async def index(service: Service = Depends(AsyncProvide[Container.service])):
    result = await service.process()
    return {"result": result}


container = Container()
container.wire(modules=[__name__])

app.state.container = container

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)