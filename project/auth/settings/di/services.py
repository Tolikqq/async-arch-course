from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

from app.application.services import UserService
from settings.config import AppSettings


class ServicesContainer(DeclarativeContainer):
    settings: providers.Dependency[AppSettings] = providers.Dependency()

    repositories = providers.DependenciesContainer()
    gateways = providers.DependenciesContainer()
    adapters = providers.DependenciesContainer()

    user_service: Singleton[UserService] = Singleton(
        UserService,
        repository=repositories.user_repository,
        event_dispatcher=adapters.user_event_dispatcher
    )
