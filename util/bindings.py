# Global
QUIT = ("q", "request_quit", "Quit")

# Active Tab
EXECUTE_QUERY = ("e", "exec_query", "Execute")
CLEAR_INPUT = ("c", "clear_input", "Clear")
FORMAT_QUERY = ("f", "format_query", "Format")

# Connection Tree
PREVIEW_DATA = ("p", "preview_data", "Preview")
REFRESH_NODE = ("r", "refresh_parent", "Refresh node")
REFRESH_CONNECTION = ("R", "refresh_connection", "Refresh connection")
NEW_CONNECTION = ("n", "request_new_connection", "New Connection")

# Containers
GLOBAL_BINDINGS = [QUIT]

QUERY_BINDINGS = [EXECUTE_QUERY, CLEAR_INPUT, FORMAT_QUERY]

CONNECTION_TREE_BINDINGS = [PREVIEW_DATA, REFRESH_NODE, REFRESH_CONNECTION, NEW_CONNECTION]

# Collected
ALL_BINDINGS = GLOBAL_BINDINGS + QUERY_BINDINGS + CONNECTION_TREE_BINDINGS


def actions(bindings: [(str, str, str)]) -> [str]:
    return list(map(lambda a: a[1], bindings))
