import sqlite3
from sqlite3 import OperationalError
import logging
from connectors.connector import Connector, ConnectorType, ExecutionStatus
from util.model import Schema, Table, Column
from string import Template

logger = logging.getLogger(__name__)


class SqliteConnector(Connector):
    TABLES_QUERY = """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
            AND name NOT LIKE 'sqlite_%';
        """
    VIEWS_QUERY = """
        SELECT name
        FROM sqlite_master
        WHERE type='view'
            AND name NOT LIKE 'sqlite_%';
        """

    COLUMNS_QUERY = Template("""
        SELECT NAME, TYPE, \"notnull\", pk, dflt_value
        FROM PRAGMA_TABLE_INFO('$table');
        """)

    def __init__(self, database):
        super().__init__(database, None, None, None, None, ConnectorType.SQLITE)
        with sqlite3.connect(self.connection_string()) as conn:
            conn.cursor()

    def connection_string(self) -> str:
        return f"{self.database}.db"

    def get_schemas(self) -> list[Schema]:
        schemas = list()
        schemas.append(Schema(self.database, None, None))
        return schemas

    def get_tables(self, schema: str) -> list[Table]:
        results = self.query(self.TABLES_QUERY)
        tables = list()
        for val in results:
            tables.append(Table(val[0], None))
        return tables

    def get_views(self, schema: str) -> list[Table]:
        results = self.query(self.VIEWS_QUERY)
        tables = list()
        for val in results:
            tables.append(Table(val[0], None))
        return tables

    def get_columns(self, schema: str, table: str) -> list[Column]:
        query: str = self.COLUMNS_QUERY.substitute(table=table)
        columns = list()
        results = self.query(query)
        for val in results:
            columns.append(Column(val[0], val[1], bool(val[2]), bool(val[3]), val[4]))
        return columns

    def execute(self, query: str) -> (ExecutionStatus, str):
        with sqlite3.connect(self.connection_string()) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                return (ExecutionStatus.Success, None)
            except Exception as e:
                logger.error(f"Error: {repr(e)}")
                return (ExecutionStatus.Failure, repr(e))

    def query(self, query: str) -> [()]:
        with sqlite3.connect(self.connection_string()) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
            except OperationalError as e:
                logger.error(f"Error: {repr(e)}")
                return [("error", repr(e))]

    def query_with_names(self, query: str) -> [()]:
        with sqlite3.connect(self.connection_string()) as conn:
            try:
                cursor = conn.cursor()
                try:
                    cursor.execute(query)
                    names = tuple(list(map(lambda x: x[0], cursor.description)))
                except TypeError:
                    names = tuple([])
                rows = cursor.fetchall()
                rows.insert(0, names)
                return rows
            except Exception as e:
                logger.error(f"Error: {repr(e)}")
                return [("error", repr(e))]
