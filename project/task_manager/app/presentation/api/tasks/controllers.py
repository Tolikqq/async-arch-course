import uuid
from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Path
from dependency_injector.wiring import Provide, inject

from app.application.command.complete_task import CompleteTaskCommand, CompleteTaskCommandProcessor
from app.application.command.create_task import CreateTaskCommandProcessor, CreateTaskCommand, CreateTaskDTO, \
    DuplicateTaskError
from app.application.command.reassign_tasks import UserDoesNotHavePermission, ReassignTasksCommandProcessor, \
    ReassignTasksCommand
from app.application.query.get_tasks import GetTasksQueryHandler, GetTasksListQuery, TaskDTO
from app.domain.task import TaskNotOpenError
from app.domain.worker import Worker
from app.infrastrucrute.di.container import DIContainer
from app.presentation.api.deps import get_current_user
from app.presentation.api.schema import OkResponse, SuccessEmptyResponse
from app.presentation.api.tasks.serializers import CreateTaskRequest

router = APIRouter()


@router.post("/tasks")
@inject
async def create_task(
        request_body: CreateTaskRequest,
        command_processor: CreateTaskCommandProcessor = Depends(Provide[DIContainer.services.create_task_command]),
        current_user: Worker = Depends(get_current_user)
) -> OkResponse[CreateTaskDTO]:
    command = CreateTaskCommand(
        task_id=uuid.UUID(request_body.task_id),
        creator_id=current_user.id,
        description=request_body.description,
        assignee_id=uuid.UUID(request_body.assignee_id),
    )
    try:
        result = await command_processor.process(command=command)
    except DuplicateTaskError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return OkResponse.new(
        status_code=status.HTTP_201_CREATED,
        model=CreateTaskDTO,
        data=result,
    )


@router.post("/tasks/reassign")
@inject
async def reassign_tasks(
        current_user: Worker = Depends(get_current_user),
        command_processor: ReassignTasksCommandProcessor = Depends(
            Provide[DIContainer.services.reassign_tasks_command]),
) -> OkResponse[BaseModel]:
    command = ReassignTasksCommand(worker_id=current_user.id)
    try:
        await command_processor.process(command=command)
    except UserDoesNotHavePermission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cant reassign tasks",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return SuccessEmptyResponse


@router.get("/my-tasks")
@inject
async def get_my_tasks(
        user: Worker = Depends(get_current_user),
        query_handler: GetTasksQueryHandler = Depends(Provide[DIContainer.services.get_tasks_query_handler])
) -> OkResponse[list[TaskDTO]]:
    data = await query_handler.handle(query=GetTasksListQuery(assignee_id=user.id))
    return OkResponse.new(
        status_code=status.HTTP_200_OK,
        model=list[TaskDTO],
        data=data,
    )


@router.post("/my-tasks/{id}/complete")
@inject
async def complete_task(
        id: Annotated[str, Path()],
        current_user: Worker = Depends(get_current_user),
        command_processor: CompleteTaskCommandProcessor = Depends(Provide[DIContainer.services.complete_task_command]),
) -> OkResponse[BaseModel]:
    command = CompleteTaskCommand(worker_id=current_user.id, task_id=uuid.UUID(id))
    try:
        await command_processor.process(command=command)
    except TaskNotOpenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task has already closed")
    else:
        return SuccessEmptyResponse
