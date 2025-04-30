import json
import os.path

from connection.conn import Conn, ConnectionEncoder
from connection.connection import Connection

FILE_PATH: str = "conn.json"

def read_conn_file() -> [Connection]:
    if os.path.isfile(FILE_PATH):
        if os.path.getsize(FILE_PATH) == 0:
            return []
        with open("conn.json", "r") as file:
            data = json.load(file)
            connections = list(map(lambda itm: Connection.from_conn(Conn.from_dict(itm)), data))
            return connections
    else:
        return []


def write_conn_file(connections: [Connection]) -> None:
    conn_arr = []
    for connection in connections:
        conn = connection.conn
        conn.encrypt()
        conn_arr.append(conn)
    with open("conn.json", "w") as file:
        file.write(json.dumps(conn_arr, cls=ConnectionEncoder))
