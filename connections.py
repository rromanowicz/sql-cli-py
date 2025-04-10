import logging
from textual.widgets import Tab, TextArea, DataTable
from dataclasses import dataclass
from enum import Enum
from connectors.connector import Connector
from connectors.sqlite_connector import SqliteConnector

logger = logging.getLogger(__name__)


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
    connected: bool = False

    def __init__(self, id: str, env: Env):
        self.id = id
        self.tab = Tab(id, id=id)
        self.input = TextArea.code_editor("SELECT * FROM Students;", language="sql")
        self.results = DataTable()
        self.conn = DbConnection("test", "", "", SqliteConnector("test"))
        self.connected = False

    def schemas(self) -> list[str]:
        self.connected = True
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
                lambda column: (
                    column.get_name(),
                    column.get_type(),
                    column.is_required(),
                ),
                self.conn.connector.columns(schema, table),
            )
        )

    def exec_query(self):
        query: str = self.input.text
        results = self.conn.connector.query_with_names(query)
        logger.info(results[1])
        if len(results) != 0:
            self.results.clear()
            self.results.columns.clear()
            self.results.add_columns(*results[0])
            self.results.add_rows(results[1:])
