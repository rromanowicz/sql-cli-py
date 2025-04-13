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
        self.env = env

    def schemas(self) -> list[str]:
        self.connected = True
        return list(
            map(lambda schema: schema.get_name(), self.conn.connector.schemas())
        )

    def tables(self, schema: str) -> list[str]:
        return list(
            map(lambda table: table.get_name(), self.conn.connector.tables(schema))
        )

    def columns(self, schema: str, table: str) -> list[(str, str, bool, bool, str)]:
        return list(
            map(
                lambda column: (
                    column.get_name(),
                    column.get_type(),
                    column.is_required(),
                    column.is_primary_key(),
                    column.get_default_value(),
                ),
                self.conn.connector.columns(schema, table),
            )
        )

    def exec_query(self):
        query: str = self.input.text
        if len(query) == 0:
            return
        if query.lower().__contains__("insert ") or query.lower().__contains__(
            "update " or query.lower().__contains__("create ")  # TODO: fix this
        ):
            result = self.conn.connector.execute(query)
            self.results.clear()
            self.results.columns.clear()
            self.results.add_columns("Status", "msg")
            self.results.add_rows([(result[0].name, result[1])])
        else:
            results = self.conn.connector.query_with_names(query)
            if len(results) != 0:
                self.results.clear()
                self.results.columns.clear()
                if len(results) == 1 and results[0][0] == "error":
                    self.results.add_columns("Status", "msg")
                    self.results.add_rows([(results[0][0], results[0][1])])
                else:
                    self.results.add_columns(*results[0])
                    self.results.add_rows(results[1:])
