from dependency_injector import containers, providers
from dependency_injector.providers import Singleton

from app.infrastructure.user_repository import UserRepository
from settings.config import AppSettings


class RepositoriesContainer(containers.DeclarativeContainer):
    settings: providers.Dependency[AppSettings] = providers.Dependency()

    adapters = providers.DependenciesContainer()
    gateways = providers.DependenciesContainer()

    user_repository = Singleton(UserRepository, db=adapters.database)
