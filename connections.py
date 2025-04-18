import logging
from textual.widgets import Tab, TextArea, DataTable
from dataclasses import dataclass
from connectors.connector import Connector, ConnectorType
from connectors.connector_resolver import resolve_connector
from model import Env
import sqlparse

logger = logging.getLogger(__name__)


@dataclass
class DbConnection:
    database: str
    host: str
    user: str
    passwd: str
    connector_type: ConnectorType
    connector: Connector

    def __init__(
        self, database: str, host: str, user: str, passwd: str, type: ConnectorType
    ) -> None:
        self.database = database
        self.host = host
        self.user = user
        self.passwd = passwd
        self.connector_type = type
        self.connector = resolve_connector(database, host, user, passwd, type)


@dataclass
class Connection:
    id: str
    tab: Tab
    input: TextArea
    results: DataTable
    conn: DbConnection
    env: Env
    connected: bool = False

    def __init__(
        self,
        id: str,
        database: str,
        host: str,
        user: str,
        passwd: str,
        type: ConnectorType,
        env: Env,
    ):
        self.id = id
        self.tab = Tab(id, id=id)
        self.input = TextArea.code_editor("select 1", language="sql")
        self.results = DataTable()
        self.conn = DbConnection(database, host, user, passwd, ConnectorType.SQLITE)
        self.connected = False
        self.env = env

    def clear(self) -> None:
        self.conn.connector.clear()

    def clear_by_type(self, type: str, schema: str, object: str = None) -> None:
        self.conn.connector.clear_by_type(type, schema, object)

    def schemas(self) -> list[str]:
        self.connected = True
        return list(
            map(lambda schema: schema.get_name(), self.conn.connector.schemas())
        )

    def tables(self, schema: str) -> list[str]:
        return list(
            map(lambda table: table.get_name(), self.conn.connector.tables(schema))
        )

    def views(self, schema: str) -> list[str]:
        return list(
            map(lambda table: table.get_name(), self.conn.connector.views(schema))
        )

    def columns(
        self, schema: str, table: str, type: str
    ) -> list[(str, str, bool, bool, str)]:
        return list(
            map(
                lambda column: (
                    column.get_name(),
                    column.get_type(),
                    column.is_required(),
                    column.is_primary_key(),
                    column.get_default_value(),
                ),
                self.conn.connector.columns(schema, table, type),
            )
        )

    def exec_query(self) -> None:
        query: str = self.input.text
        parsed = sqlparse.parse(query)
        if len(parsed) == 0:
            return
        self.results.clear()
        self.results.columns.clear()
        if parsed[0].get_type() in ["CREATE", "DROP", "INSERT", "UPDATE"]:
            result = self.conn.connector.execute(query)
            self.results.add_columns("Status", "msg")
            self.results.add_rows([(result[0].name, result[1])])
        elif parsed[0].get_type() in ["SELECT"]:
            results = self.conn.connector.query_with_names(query)
            if len(results) != 0:
                if len(results) == 1 and results[0][0] == "error":
                    self.results.add_columns("Status", "msg")
                    self.results.add_rows([(results[0][0], results[0][1])])
                else:
                    self.results.add_columns(*results[0])
                    self.results.add_rows(results[1:])
        elif parsed[0].get_type() in ["UNKNOWN"]:
            self.results.add_columns("Status", "msg")
            self.results.add_rows(
                [
                    ("Error", "Unknown query type"),
                    ("", "Raise a bug if the query is valid."),
                ]
            )
        else:
            self.results.add_columns("Status", "msg")
            self.results.add_rows(
                [
                    ("Error", "Unhandled query type"),
                    ("QueryType", f"{parsed[0].get_type()}"),
                ]
            )

    def format_query(self) -> None:
        query: str = self.input.text
        formatted = sqlparse.format(query, reindent=True, keyword_case="upper")
        self.input.text = formatted
