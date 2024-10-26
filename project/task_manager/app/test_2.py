from dataclasses import dataclass
from dependency_injector import containers, providers


def resource():
    print("init")
    yield "res"
    print("stop")


class Database: ...


@dataclass
class UserService:
    db: Database
    resource: str


class FakeDB: ...


class Container(containers.DeclarativeContainer):
    database = providers.Singleton(Database)
    resource = providers.Resource(resource)
    user_service = providers.Singleton(UserService, db=database, resource=resource)


if __name__ == "__main__":
    container = Container()
    print(container.user_service().db)
    # container.reset_singletons()
    with container.database.override(FakeDB()):
        print(container.user_service().db)