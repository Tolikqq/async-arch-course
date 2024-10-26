


from fastapi import APIRouter, BackgroundTasks
from dependency_injector.wiring import Provide, inject

from app.infrastrucrute.di.container import DIContainer
from app.infrastrucrute.outbox.message_relay import OutboxProcessor

router = APIRouter()


@inject
async def start_outbox_scheduler(
        outbox_processor: OutboxProcessor = Provide[DIContainer.kafka_handlers.outbox_processor]
) -> None:
    await outbox_processor.run()


@router.post("/start-outbox")
async def start_pull_outbox(background_tasks: BackgroundTasks) -> dict[str, str]:
    """
    I don't want to use any library and broker for outbox pulling
    """
    background_tasks.add_task(start_outbox_scheduler)
    return {"message": "Outbox processor in the background"}