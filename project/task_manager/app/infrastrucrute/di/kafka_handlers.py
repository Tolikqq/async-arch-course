from dependency_injector import containers, providers
from dependency_injector.providers import Singleton
from app.application.events.account_changes import AccountChangesEventHandler
from app.application.events.task_worker_notifier import NotifyWhenTaskAssignedEventHandler
from app.infrastrucrute.outbox.event_dispather import OutboxEventDispatcher
from app.infrastrucrute.outbox.message_relay import OutboxProcessor
from settings.config import AppSettings


class KafkaHandlersContainer(containers.DeclarativeContainer):
    settings: providers.Dependency[AppSettings] = providers.Dependency()

    services = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()
    gateways = providers.DependenciesContainer()
    adapters = providers.DependenciesContainer()

    account_changes_event_handler: Singleton[AccountChangesEventHandler] = Singleton(
        AccountChangesEventHandler,
        repository=repositories.worker_repository,
    )

    task_assigned_event_handler: Singleton[NotifyWhenTaskAssignedEventHandler] = Singleton(
        NotifyWhenTaskAssignedEventHandler,
        producer=adapters.kafka_avro_adapter,
        email_notification_gateway=gateways.email_notification_gateway,
        worker_repository=repositories.worker_repository,
    )

    outbox_event_dispatcher: Singleton[OutboxEventDispatcher] = Singleton(
        OutboxEventDispatcher,
        task_assigned_event_handler=task_assigned_event_handler
    )

    outbox_processor: Singleton[OutboxProcessor] = Singleton(
        OutboxProcessor,
        outbox_repository=repositories.outbox_repository,
        event_dispatcher=outbox_event_dispatcher,
    )
