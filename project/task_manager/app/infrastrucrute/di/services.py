from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

from app.application.command.complete_task import CompleteTaskCommandProcessor
from app.application.command.create_task import CreateTaskCommandProcessor
from app.application.command.reassign_tasks import ReassignTasksCommandProcessor
from app.application.query.get_tasks import GetTasksQueryHandler
from app.application.worker_service import WorkerService
from app.infrastrucrute.task_dispatcher import TaskEventDispatcher
from settings.config import AppSettings


class ServicesContainer(DeclarativeContainer):
    settings: providers.Dependency[AppSettings] = providers.Dependency()

    repositories = providers.DependenciesContainer()
    gateways = providers.DependenciesContainer()
    adapters = providers.DependenciesContainer()

    task_event_dispatcher: Singleton[TaskEventDispatcher] = Singleton(
        TaskEventDispatcher,
        producer=adapters.kafka_avro_adapter,
    )

    get_tasks_query_handler: Singleton[GetTasksQueryHandler] = Singleton(
        GetTasksQueryHandler,
        db=adapters.database
    )

    create_task_command: Singleton[CreateTaskCommandProcessor] = Singleton(
        CreateTaskCommandProcessor,
        repository=repositories.task_repository,
        outbox_repository=repositories.outbox_repository,
    )

    reassign_tasks_command: Singleton[ReassignTasksCommandProcessor] = Singleton(
        ReassignTasksCommandProcessor,
        repository=repositories.task_repository,
        outbox_repository=repositories.outbox_repository,
    )

    complete_task_command: Singleton[CompleteTaskCommandProcessor] = Singleton(
        CompleteTaskCommandProcessor,
        repository=repositories.task_repository,
        event_dispatcher=task_event_dispatcher
    )

    worker_service: Singleton[WorkerService] = Singleton(
        WorkerService,
        repository=repositories.worker_repository
    )

