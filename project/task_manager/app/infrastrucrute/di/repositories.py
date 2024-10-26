from dependency_injector import containers, providers
from dependency_injector.providers import Singleton

from app.infrastrucrute.outbox.repositories import OutboxRepository
from app.infrastrucrute.repositories.task_repository import TaskRepository
from app.infrastrucrute.repositories.worker_repository import WorkerRepository
from settings.config import AppSettings


class RepositoriesContainer(containers.DeclarativeContainer):
    settings: providers.Dependency[AppSettings] = providers.Dependency()

    adapters = providers.DependenciesContainer()

    outbox_repository: Singleton[OutboxRepository] = Singleton(OutboxRepository, session=adapters.database.provided.session)

    worker_repository = Singleton(WorkerRepository, session=adapters.database.provided.session)
    task_repository = Singleton(TaskRepository, session=adapters.database.provided.session)