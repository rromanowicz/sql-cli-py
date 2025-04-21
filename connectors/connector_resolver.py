from connectors.connector import ConnectorType, Connector
from connectors.sqlite_connector import SqliteConnector
from connectors.postgres_connector import PostgreSqlConnector
from connectors.dummy_connector import DummyConnector
from connectors.exceptions import NewConnectionError


def resolve_connector(
    database: str, host: str, port, user: str, passw: str, type: ConnectorType
) -> Connector:
    match type:
        case ConnectorType.POSTGRESQL:
            required_fields_check(
                {"Database": database, "Host": host, "Port": port, "User": user, "Password": passw}
            )
            return PostgreSqlConnector(database, host, port, user, passw)
        case ConnectorType.SQLITE:
            required_fields_check({"Database": database})
            return SqliteConnector(database)
        case _:
            return DummyConnector()


def required_fields_check(args: dict[str, any]) -> bool:
    errors = []
    for key, value in args.items():
        if isinstance(value, str):
            if value is None or len(value) == 0:
                errors.append(key)
        else:
            if value is None:
                errors.append(key)

    if len(errors) != 0:
        message = ""
        for val in errors:
            message += f"\n'{val}' field is required."
        raise NewConnectionError(message)
