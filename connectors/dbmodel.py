from dataclasses import dataclass


@dataclass
class Column:
    name: str
    type: str
    required: bool

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return self.type

    def is_required(self) -> bool:
        return self.required

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

    def get_name(self) -> str:
        return self.name
