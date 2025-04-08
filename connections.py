from textual.widgets import Tab, TextArea, DataTable
from dataclasses import dataclass
from enum import Enum
from connectors.connector import Connector
from connectors.dummy_connector import DummyConnector


class Env(Enum):
    DEV = 1
    SIT = 2
    SAT = 3
    PROD = 4


@dataclass
class DbConnection:
    user: str
    passwd: str
    connector: Connector


@dataclass
class Connection:
    id: str
    tab: Tab
    input: TextArea
    results: DataTable
    conn: DbConnection
    env: Env

    def __init__(self, id: str, env: Env):
        self.id = id
        self.tab = Tab(id, id=id)
        self.input = TextArea.code_editor("SELECT * FROM DUAL;", language="sql")
        self.results = DataTable()
        self.conn = DbConnection("", "", DummyConnector)
