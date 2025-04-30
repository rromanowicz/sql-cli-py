import logging

import sqlparse
from textual.widgets import DataTable, Tab, TextArea

from connection.conn import Conn
from connectors.connector import Connector

logger = logging.getLogger(__name__)


class Connection:
    """
    Connection handler
    """

    id: str
    tab: Tab
    input: TextArea
    results: DataTable
    conn: Conn
    connector: Connector
    connected: bool = False

    def __init__(self, conn: Conn):
        self.id = conn.id  # conn.uid()
        self.tab = Tab(conn.id, id=conn.id)
        self.input = TextArea.code_editor("select 1", language="sql")
        self.results = DataTable()
        self.conn = conn
        self.connector = self.conn.connector()
        self.connected = False

    @classmethod
    def from_conn(self, conn: Conn):
        return self(conn)

    def clear(self) -> None:
        self.connector.clear()

    def clear_by_type(self, type: str, schema: str, object: str = None) -> None:
        self.connector.clear_by_type(type, schema, object)

    def schemas(self) -> list[str]:
        self.connected = True
        return list(map(lambda schema: schema.get_name(), self.connector.schemas()))

    def tables(self, schema: str) -> list[str]:
        return list(map(lambda table: table.get_name(), self.connector.tables(schema)))

    def views(self, schema: str) -> list[str]:
        return list(map(lambda table: table.get_name(), self.connector.views(schema)))

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
                self.connector.columns(schema, table, type),
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
            result = self.connector.execute(query)
            self.results.add_columns("Status", "msg")
            self.results.add_rows([(result[0].name, result[1])])
        elif parsed[0].get_type() in ["SELECT"]:
            results = self.connector.query_with_names(query)
            if results and len(results) != 0:
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

    def exec_preview(self, schema: str, table: str) -> None:
        self.clear()
        self.input.text = self.connector.preview_query(schema, table)
        self.format_query()
        self.exec_query()

    def test(self) -> None:
        self.connector.test()

    def format_query(self) -> None:
        query: str = self.input.text
        formatted = sqlparse.format(query, reindent=True, keyword_case="upper")
        self.input.text = formatted
