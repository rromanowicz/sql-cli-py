from enum import Enum
from dataclasses import dataclass


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Env(ExtendedEnum):
    DEV = "DEV"
    SIT = "SIT"
    SAT = "SAT"
    PROD = "PROD"


class ConnectorType(ExtendedEnum):
    SQLITE = "SqLite"
    DUMMY = "Dummy"


class ExecutionStatus(Enum):
    Success = 1
    Failure = 2


@dataclass
class Column:
    name: str
    type: str
    required: bool
    primary_key: bool
    default_value: str

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return self.type

    def is_required(self) -> bool:
        return self.required

    def is_primary_key(self) -> bool:
        return self.primary_key

    def get_default_value(self) -> str:
        return self.default_value

    def __repr__(self) -> str:
        return f"{self.name.capitalize()} ({self.type.capitalize()})"


@dataclass
class Table:
    name: str
    columns: dict[str, Column]

    def get_name(self) -> str:
        return self.name


@dataclass
class Schema:
    name: str
    tables: dict[str, Table]
    views: dict[str, Table]

    def get_name(self) -> str:
        return self.name
