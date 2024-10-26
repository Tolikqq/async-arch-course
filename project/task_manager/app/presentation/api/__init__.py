from fastapi import APIRouter
from app.presentation.api.tasks import controllers as task_controllers
from app.presentation.api import cron_outbox_controller as outbox

router = APIRouter()
router.include_router(task_controllers.router)
router.include_router(outbox.router)
