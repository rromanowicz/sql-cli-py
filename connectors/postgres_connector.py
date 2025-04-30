import logging
from string import Template

import psycopg

from connectors.connector import Connector, ConnectorType, ExecutionStatus
from connectors.exceptions import NewConnectionError
from util.model import Column, Schema, Table

logger = logging.getLogger(__name__)


class PostgreSqlConnector(Connector):
    SCHEMAS_QUERY = "SELECT SCHEMA_NAME AS NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_OWNER='pg_database_owner';"
    TABLES_QUERY = Template(
        "SELECT TABLE_NAME AS NAME FROM INFORMATION_SCHEMA.\"tables\" WHERE TABLE_SCHEMA = '$schema' and TABLE_TYPE='BASE TABLE';"
    )
    VIEWS_QUERY = Template(
        "SELECT TABLE_NAME AS NAME FROM INFORMATION_SCHEMA.\"tables\" WHERE TABLE_SCHEMA = '$schema' and TABLE_TYPE='VIEW';"
    )
    COLUMNS_QUERY = Template(
        "SELECT COLUMN_NAME AS NAME, DATA_TYPE AS TYPE FROM INFORMATION_SCHEMA.\"columns\" WHERE TABLE_SCHEMA='$schema' AND TABLE_NAME ='$table';"
    )
    COLUMNS_QUERY = Template("""
        SELECT COLUMN_NAME AS NAME, DATA_TYPE AS TYPE
            , CASE WHEN IS_NULLABLE = 'YES' THEN 0 ELSE 1 END AS NOT_NULL
            , (SELECT INDISPRIMARY FROM PG_INDEX WHERE INDRELID = '$table'::REGCLASS) AS PK
            , COLUMN_DEFAULT AS DEFAULT_VALUE
        FROM INFORMATION_SCHEMA."columns"
        WHERE TABLE_SCHEMA='$schema'
            AND TABLE_NAME ='$table';
        """)

    PREVIEW_QUERY = Template("""SELECT * FROM $schema.$table LIMIT 10;
    """)

    def __init__(self, database: str, host: str, port: int, user: str, passw: str):
        super().__init__(database, host, port, user, passw, ConnectorType.POSTGRESQL)

    def test(self) -> None:
        try:
            with psycopg.connect(self.connection_string()) as conn:
                conn.cursor()
        except Exception as e:
            raise NewConnectionError(e.__str__())

    def connection_string(self) -> str:
        return f"dbname={self.database} host={self.host} port={self.port} user={self.user} password={self.passw}"

    def get_schemas(self) -> list[Schema]:
        results = self.query(self.SCHEMAS_QUERY)
        schemas = list()
        for val in results:
            schemas.append(Schema(val[0], None, None))
        return schemas

    def get_tables(self, schema: str) -> list[Table]:
        query: str = self.TABLES_QUERY.substitute(schema=schema)
        results = self.query(query)
        tables = list()
        for val in results:
            tables.append(Table(val[0], None))
        return tables

    def get_views(self, schema: str) -> list[Table]:
        query: str = self.VIEWS_QUERY.substitute(schema=schema)
        logger.info(query)
        results = self.query(query)
        tables = list()
        for val in results:
            tables.append(Table(val[0], None))
        return tables

    def get_columns(self, schema: str, table: str) -> list[Column]:
        query: str = self.COLUMNS_QUERY.substitute(schema=schema, table=table)
        columns = list()
        results = self.query(query)
        for val in results:
            columns.append(Column(val[0], val[1], bool(val[2]), bool(val[3]), val[4]))
        return columns

    def preview_query(self, schema: str, table: str) -> str:
        return self.PREVIEW_QUERY.substitute(schema=schema, table=table)

    def execute(self, query: str) -> (ExecutionStatus, str):
        with psycopg.connect(self.connection_string()) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(query)
                    return (ExecutionStatus.Success, None)
                except Exception as e:
                    logger.error(f"Error: {repr(e)}")
                    return (ExecutionStatus.Failure, repr(e))

    def query(self, query: str) -> [()]:
        with psycopg.connect(self.connection_string()) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(query)
                    return cur.fetchall()
                except Exception as e:
                    logger.error(f"Error: {repr(e)}")
                    return [("error", repr(e))]

    def query_with_names(self, query: str) -> [()]:
        with psycopg.connect(self.connection_string()) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(query)
                    names = tuple(list(map(lambda x: x[0], cur.description)))
                    rows = cur.fetchall()
                    rows.insert(0, names)
                    return rows
                except Exception as e:
                    logger.error(f"Error: {repr(e)}")
                    return [("error", repr(e))]
