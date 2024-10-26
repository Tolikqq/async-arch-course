from dependency_injector import containers
from dependency_injector.providers import (
    Callable,
    Container, Configuration,
)

from settings.config import get_settings
from settings.di.adapters import AdaptersContainer
from settings.di.repositories import RepositoriesContainer
from settings.di.services import ServicesContainer


class DIContainer(containers.DeclarativeContainer):
    config = Configuration()

    settings = Callable(get_settings)

    adapters = Container(AdaptersContainer, settings=settings)
    # gateways = Container(GatewaysContainer, settings=settings, adapters=adapters)
    repositories = Container(RepositoriesContainer, settings=settings, adapters=adapters)
    services = Container(
        ServicesContainer, settings=settings, repositories=repositories, adapters=adapters
    )