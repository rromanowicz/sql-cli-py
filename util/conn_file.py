from connections import Connection, ConnectionEncoder
import json
import os.path


def read_conn_file() -> [Connection]:
    if os.path.isfile("conn.json"):
        with open("conn.json", "r") as file:
            data = json.load(file)
            connections = list(map(lambda itm: Connection.from_dict(itm), data))
            return connections
    else:
        with open("conn.json", "w") as file:
            file.write("[]")
        return []


def write_conn_file(connections: [Connection]) -> None:
    for conn in connections:
        conn.encrypt()
    with open("conn.json", "w") as file:
        file.write(json.dumps(connections, cls=ConnectionEncoder))
