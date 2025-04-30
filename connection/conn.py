from dataclasses import dataclass
from json import JSONEncoder

import util.crypto as C
from connectors.connector import Connector, ConnectorType
from connectors.connector_resolver import resolve_connector
from connectors.exceptions import NewConnectionError
from util.model import Env


@dataclass
class Conn:
    """
    Connection details
    """
    id: str
    database: str
    host: str
    port: int
    user: str
    passwd: str
    connector_type: ConnectorType
    env: Env

    def __init__(
        self,
        id: str,
        database: str,
        host: str,
        port: int,
        user: str,
        passwd: str,
        connector_type: ConnectorType,
        env: Env,
    ) -> None:
        if id is None or len(id) == 0:
            raise NewConnectionError("'Name' field is required")

        self.id = id
        self.database = database
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.connector_type = connector_type
        self.env = env

    def connector(self) -> Connector:
        return resolve_connector(
            self.database,
            self.host,
            self.port,
            self.user,
            self.passwd,
            self.connector_type,
        )

    @classmethod
    def from_dict(self, input: str):
        id: str = input.get("id")
        database: str = C.decrypt(input.get("database"))
        host: str = C.decrypt(input.get("host"))
        port: int = 0 if input.get("port") is None else input.get("port")
        user: str = C.decrypt(input.get("user"))
        passwd: str = C.decrypt(input.get("password"))
        connector_type: str = str(input.get("type")).upper()
        env: str = str(input.get("env"))
        return self(
            id,
            database,
            host,
            port,
            user,
            passwd,
            ConnectorType[connector_type],
            Env[env],
        )

    def encrypt(self) -> None:
        self.database = C.encrypt(self.database)
        self.host = C.encrypt(self.host)
        self.user = C.encrypt(self.user)
        self.passwd = C.encrypt(self.passwd)

    def uid(self) -> str:
        return f"{self.id}_{self.env.value}_{self.database}_{self.user}".lower()


class ConnectionEncoder(JSONEncoder):
    def default(self, obj: Conn):
        return {
            "id": obj.id,
            "database": obj.database,
            "host": obj.host,
            "port": obj.port,
            "user": obj.user,
            "passwd": obj.passwd,
            "type": obj.connector_type.name,
            "env": obj.env.name,
        }
