from dependency_injector import containers
from dependency_injector.providers import (
    Callable, Configuration, Container,
)
from app.infrastrucrute.di.apaters import AdaptersContainer
from app.infrastrucrute.di.gateways import GatewaysContainer
from app.infrastrucrute.di.kafka_handlers import KafkaHandlersContainer
from app.infrastrucrute.di.repositories import RepositoriesContainer
from app.infrastrucrute.di.services import ServicesContainer
from settings.config import get_settings


class DIContainer(containers.DeclarativeContainer):
    config = Configuration()

    settings = Callable(get_settings)

    adapters = Container(AdaptersContainer, settings=settings)
    gateways = Container(GatewaysContainer, settings=settings, adapters=adapters)
    repositories = Container(RepositoriesContainer, settings=settings, adapters=adapters)
    services = Container(
        ServicesContainer, settings=settings, repositories=repositories, adapters=adapters
    )

    kafka_handlers = Container(
        KafkaHandlersContainer,
        services=services,
        repositories=repositories,
        gateways=gateways,
        adapters=adapters,
        settings=settings,
    )


