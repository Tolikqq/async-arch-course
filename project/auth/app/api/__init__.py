from fastapi import APIRouter
from app.api import controllers

router = APIRouter()
router.include_router(controllers.router, prefix="/iam", tags=["users"])
