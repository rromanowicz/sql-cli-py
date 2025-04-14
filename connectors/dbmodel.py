from dataclasses import dataclass


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
