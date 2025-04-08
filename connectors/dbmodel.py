from dataclasses import dataclass


@dataclass
class Column:
    name: str
    type: str


@dataclass
class Table:
    name: str
    columns: dict[str, Column]


@dataclass
class Schema:
    name: str
    tables: dict[str, Table]
