from connectors.connector import ConnectorType, Connector
from connectors.sqlite_connector import SqliteConnector
from connectors.dummy_connector import DummyConnector


def resolve_connector(
    database: str, host: str, user: str, passw: str, type: ConnectorType
) -> Connector:
    match type:
        case ConnectorType.SQLITE:
            return SqliteConnector(database)
        case _:
            return DummyConnector()
