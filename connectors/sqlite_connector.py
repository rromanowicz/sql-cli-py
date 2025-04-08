import sqlite3
from connectors.connector import Connector, Type
from connectors.dbmodel import Schema, Table, Column


class SqliteConnector(Connector):
    def __init__(self, database):
        super().__init__(database, None, None, None, Type.SqLite)
        self.schemas_callable = self.get_schemas
        self.tables_callable = self.get_tables
        self.columns_callable = self.get_columns
        with sqlite3.connect(self.connection_string()) as conn:
            conn.cursor()

    def connection_string(self) -> str:
        return f"{self.database}.db"

    def get_schemas(self) -> list[Schema]:
        schemas = list()
        schemas.append(Schema(self.database, None))
        return schemas

    def get_tables(self, schema: str) -> list[Table]:
        query: str = """
            SELECT name
            FROM sqlite_master
                WHERE type='table'
                AND name NOT LIKE 'sqlite_%';
        """
        results = self.query(query)
        tables = list()
        for val in results:
            tables.append(Table(val[0], None))
        return tables

    def get_columns(self, schema: str, table: str) -> list[Column]:
        query: str = f"SELECT NAME, TYPE FROM PRAGMA_TABLE_INFO('{table}')"
        columns = list()
        results = self.query(query)
        for val in results:
            columns.append(Column(val[0], val[1]))
        return columns

    def execute(self, query: str) -> None:
        with sqlite3.connect(self.connection_string()) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
        return None

    def query(self, query: str) -> [()]:
        with sqlite3.connect(self.connection_string()) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
