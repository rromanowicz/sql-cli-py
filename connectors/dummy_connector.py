from connectors.connector import Connector, ConnectorType
from model import Schema, Table, Column


DUMMY_DATA = data = {
    "public": {
        "users": {"id": "long", "name": "string"},
        "something": {"id": "long", "test": "number"},
    },
    "test": {
        "test": {"id": "long", "test_name": "string"},
        "more_tests": {"id": "long", "test_count": "number"},
    },
}


class DummyConnector(Connector):
    def __init__(self):
        super().__init__(None, None, None, None, ConnectorType.DUMMY)

    def connection_string(self) -> str:
        return f"{self.user}:{self.passw}@{self.host}/{self.database}"

    def schemas(self) -> list[Schema]:
        schemas = list()
        for key, value in DUMMY_DATA:
            schemas.append(Schema(key, self.tables(key)))
        return schemas

    def tables(self, schema: str) -> list[Table]:
        tables = list()
        for key, value in DUMMY_DATA.get(str):
            tables.append(Table(key, self.columns(schema, key)))
        return tables

    def columns(self, schema: str, table: str) -> list[Column]:
        columns = list()
        for key, value in DUMMY_DATA.get(schema).get(table):
            columns.append(Column(key, value))
        return columns

    def execute(self, query: str) -> None:
        return None

    def query(self, query: str) -> [()]:
        return [
            ("lane", "swimmer", "country", "time"),
            (4, "Joseph Schooling", "Singapore", 50.39),
            (2, "Michael Phelps", "United States", 51.14),
            (5, "Chad le Clos", "South Africa", 51.14),
            (6, "László Cseh", "Hungary", 51.14),
            (3, "Li Zhuhao", "China", 51.26),
            (8, "Mehdy Metella", "France", 51.58),
            (7, "Tom Shields", "United States", 51.73),
            (1, "Aleksandr Sadovnikov", "Russia", 51.84),
            (10, "Darren Burns", "Scotland", 51.84),
        ]
