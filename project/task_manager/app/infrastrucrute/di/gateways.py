from dependency_injector import containers, providers
from dependency_injector.providers import Singleton

from app.infrastrucrute.gateways.email_notification import EmailNotificationGateway
from settings.config import AppSettings


class GatewaysContainer(containers.DeclarativeContainer):
    settings: providers.Dependency[AppSettings] = providers.Dependency()

    adapters = providers.DependenciesContainer()

    email_notification_gateway: Singleton[EmailNotificationGateway] = Singleton(
        EmailNotificationGateway,
        smtp_adapter=adapters.smtp_adapter,
    )
