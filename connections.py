from textual.widgets import Tab, TextArea, DataTable
from dataclasses import dataclass
from enum import Enum
from connectors.connector import Connector
from connectors.sqlite_connector import SqliteConnector


class Env(Enum):
    DEV = 1
    SIT = 2
    SAT = 3
    PROD = 4


@dataclass
class DbConnection:
    database: str
    user: str
    passwd: str
    connector: Connector


@dataclass
class Connection:
    id: str
    tab: Tab
    input: TextArea
    results: DataTable
    conn: DbConnection
    env: Env

    def __init__(self, id: str, env: Env):
        self.id = id
        self.tab = Tab(id, id=id)
        self.input = TextArea.code_editor("SELECT * FROM DUAL;", language="sql")
        self.results = DataTable()
        self.conn = DbConnection("test", "", "", SqliteConnector("test"))

    def schemas(self) -> list[str]:
        return list(
            map(lambda schema: schema.get_name(), self.conn.connector.schemas())
        )

    def tables(self, schema: str) -> list[str]:
        return list(
            map(lambda table: table.get_name(), self.conn.connector.tables(schema))
        )

    def columns(self, schema: str, table: str) -> list[(str, str, bool)]:
        return list(
            map(
                lambda column: (column.get_name(), column.get_type(), column.is_required()),
                self.conn.connector.columns(schema, table),
            )
        )
