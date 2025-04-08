from dataclasses import dataclass
from abc import ABC, abstractmethod
from connectors.dbmodel import Schema, Table, Column
from enum import Enum
from typing import Callable


class Type(Enum):
    Dummy = 1
    SqLite = 2


@dataclass
class Connector(ABC):
    def __init__(self, database: str, host: str, user: str, passw: str, type: Type):
        self.database = database
        self.host = host
        self.user = user
        self.passw = passw
        self.type = type
        self.schema_dict: dict[str, Schema] = dict()
        self.schemas_callable: Callable[[], list[Schema]] = None
        self.tables_callable: Callable[[str], list[Table]] = None
        self.columns_callable: Callable[[str, str], list[Column]] = None

    @property
    @abstractmethod
    def connection_string(self) -> str:
        pass

    def schemas(self) -> list[Schema]:
        if len(self.schema_dict) == 0:
            result: dict[str, Schema] = dict()
            for itm in self.schemas_callable():
                result[itm.name.lower()] = itm
            self.schema_dict = result
        return list(self.schema_dict.values())

    def tables(self, schema: str) -> list[Table]:
        self.schemas()
        val: Schema = self.schema_dict.get(schema.lower())
        if val.tables is None:
            tmp: dict[str, Table] = dict()
            for itm in self.tables_callable(val.name):
                tmp[itm.name.lower()] = itm
            val.tables = tmp
        self.schema_dict[schema] = val
        return list(self.schema_dict.get(schema).tables.values())

    def columns(self, schema: str, table: str) -> list[Column]:
        self.schemas()
        self.tables(schema)
        sch: Schema = self.schema_dict.get(schema.lower())
        tbl: Table = sch.tables.get(table.lower())
        if tbl.columns is None:
            tbl.columns = self.columns_callable(schema, table)
        return list(self.schema_dict.get(schema).tables.get(table.lower()).columns)

    @abstractmethod
    def execute(self, query: str) -> None:
        pass

    @abstractmethod
    def query(self, quesy: str) -> [()]:
        pass
