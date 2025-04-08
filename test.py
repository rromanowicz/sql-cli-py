from connectors.connector import Connector
from connectors.sqlite_connector import SqliteConnector

DDL = """
    CREATE TABLE IF NOT EXISTS Students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        email TEXT
    );
"""

INSERT = """
INSERT INTO Students (name, age, email)
VALUES ('John Doe', 20, 'johndoe@example.com');
"""


def main():
    connector: Connector = SqliteConnector("test")
    # connector.execute(DDL)
    # connector.execute(INSERT)

    # print(connector.schemas())
    # print(connector.tables("test"))
    print(connector.columns("test", "students"))
    # print(connector.schemas())
    print(connector.tables("test"))


main()
