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
    connector.execute(DDL)
    # connector.execute(INSERT)

    # print(connector.schemas())
    # print(connector.tables("test"))
    # print(connector.columns("test", "students"))
    # print(connector.schemas())
    # print(connector.tables("test"))

    # print(connector.execute("select * from test"))
    # print(connector.query("SELECT NAME, TYPE, \"notnull\" FROM PRAGMA_TABLE_INFO('Students')"))
    print(connector.query("select * from students"))
    print(connector.query_with_names("select * from students"))


main()
