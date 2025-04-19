from rich.text import Text
from textual.app import App
from textual.widgets import Tree

from textual.widgets._tree import TreeNode
from connections import Connection, Env


class Menu(App):
    SCHEMA = "[s]"
    TABLE = "[t]"
    VIEW = "[v]"
    SEQUENCE = "[sq]"
    COLUMN = "[c]"
    TABLES = "[T]"
    VIEWS = "[V]"
    SEQUENCES = "[SQ]"
    tree: Tree[str] = []

    def __init__(self, connections: [Connection]) -> None:
        super().__init__()
        self.connections = connections
        self.set_tree(Tree("Connections"))
        self.tree.root.expand()

        for connection in connections:
            txt: Text = Text()
            txt.append(
                f"[{connection.env.name.upper()}] ",
                style=f"bold {self.get_env_color(connection.env)}",
            )
            txt.append(connection.id)
            self.tree.root.add(txt)

    def get_env_color(self, env: Env) -> str:
        match env:
            case Env.DEV:
                return "green"
            case Env.SIT:
                return "yellow1"
            case Env.SAT:
                return "dark_orange"
            case Env.PROD:
                return "red"

    def set_tree(self, tree: Tree[str]):
        self.tree = tree

    def fill_child_nodes(self, event: Tree.NodeExpanded) -> Connection:
        if len(event.node.children) == 0:
            label: str = event.node.label.plain
            if label.startswith("["):
                parent_label = event.node.parent.label.plain
                conn: Connection = self.get_connection_by_node(event.node)
                prefix = label.split(" ")[0]
                match prefix:
                    case self.SCHEMA:
                        event.node.add(
                            Text().append("[T] ", style="turquoise2").append("Tables")
                        )
                        event.node.add(
                            Text().append("[V] ", style="turquoise2").append("Views")
                        )
                        event.node.add(
                            Text()
                            .append("[Sq] ", style="turquoise2")
                            .append("Sequences", style="s")
                        )
                    case self.TABLE | self.VIEW | self.TABLES | self.VIEWS:
                        match prefix:
                            case self.TABLE | self.TABLES:
                                type = "table"
                                prefix = self.TABLE
                            case self.VIEW | self.VIEWS:
                                type = "view"
                                prefix = self.VIEW
                        if parent_label[:3] == self.SCHEMA:
                            match type:
                                case "table":
                                    objects = conn.tables(
                                        self.strip_decorator(parent_label)
                                    )
                                case "view":
                                    objects = conn.views(
                                        self.strip_decorator(parent_label)
                                    )
                            for table_name in objects:
                                event.node.add(
                                    Text()
                                    .append(f"{prefix} ", style="turquoise2")
                                    .append(table_name)
                                )
                        else:
                            for column_def in conn.columns(
                                self.strip_decorator(
                                    event.node.parent.parent.label.plain
                                ),
                                self.strip_decorator(label),
                                type,
                            ):
                                txt: Text = (
                                    Text()
                                    .append(f"{self.COLUMN} ", style="turquoise2")
                                    .append(column_def[0])
                                )
                                if column_def[2]:
                                    txt.append(" ").append("NULL", style="red s")
                                if column_def[3]:
                                    txt.append(" ").append("PK", style="red")
                                column = event.node.add(txt)
                                column.add_leaf(column_def[1])

                                if column_def[2]:
                                    column.add_leaf(
                                        Text().append("NOT NULL", style="yellow1")
                                    )
                                if column_def[3]:
                                    column.add_leaf(
                                        Text().append("PRIMARY KEY", style="yellow1")
                                    )
                    case _:
                        if event.node.parent is not None and event.node.parent.is_root:
                            conn: Connection = self.get_connection_by_node(event.node)
                            for schema_name in conn.schemas():
                                txt: Text = (
                                    Text()
                                    .append(f"{self.SCHEMA} ", style="turquoise2")
                                    .append(schema_name)
                                )
                                event.node.add(txt)
                return Connection
            return None

    def get_connection_by_node(self, node: TreeNode) -> Connection:
        base_name: str = self.get_base_node(node).label.plain
        return self.get_connection_by_name(base_name)

    def get_base_node(self, node: TreeNode) -> TreeNode:
        parent_node: TreeNode = node.parent
        if parent_node.is_root:
            return node
        else:
            return self.get_base_node(parent_node)

    def get_parent_node_by_type(self, node: TreeNode, node_type: [str]) -> TreeNode:
        if node.is_root:
            return None
        else:
            if node.label.plain.split(" ")[0] in node_type:
                return node
            else:
                return self.get_parent_node_by_type(node.parent, node_type)

    def get_schema_node(self, node: TreeNode) -> TreeNode:
        if node.is_root:
            return None
        else:
            if node.label.plain.split(" ")[0] == self.SCHEMA:
                return node
            else:
                return self.get_schema_node(node.parent)

    def get_connection_by_name(self, name: str) -> Connection:
        for connection in self.connections:
            if self.strip_decorator(name) == connection.id:
                return connection

    def strip_decorator(self, name: str) -> str:
        if name is None or not name.startswith("["):
            return name
        return name.split(" ")[1]

    def get_refresh_type(self, node: TreeNode) -> (str, str, str):
        schema_node: TreeNode = self.get_schema_node(node)
        if not schema_node:
            return None

        schema: str = schema_node.label.plain
        type: str = None
        obj: str = None
        active_type = node.label.plain.split(" ")
        parent_type = node.parent.label.plain.split(" ")
        if len(active_type) == 1 or len(parent_type) == 1:
            return None
        else:
            if active_type[0] == parent_type[0]:
                match active_type[0]:
                    case self.TABLE:
                        type = "tables"
                    case self.VIEW:
                        type = "views"
            else:
                match parent_type[0]:
                    case self.SCHEMA:
                        type = "schema"
                    case self.TABLE:
                        type = "table"
                        obj = node.parent.label.plain
                    case self.VIEW:
                        type = "view"
                        obj = node.parent.label.plain
                    case self.COLUMN:
                        parent = self.get_refresh_type(node.parent)
                        type = parent[0]
                        obj = parent[2]
                    case _:
                        return None
        return (type, self.strip_decorator(schema), self.strip_decorator(obj))

    def refresh_connection(self) -> None:
        tree: Tree = self.app.query_one(Tree)
        active_node: TreeNode = tree.cursor_node
        if active_node is None or active_node.is_root:
            return
        self.get_connection_by_node(active_node).clear()
        base_node: TreeNode = self.get_base_node(active_node)
        base_node.remove_children()
        base_node.collapse()
        tree.select_node(base_node)

    def refresh_parent(self) -> None:
        tree: Tree = self.app.query_one(Tree)
        active_node: TreeNode = tree.cursor_node
        if active_node is None or active_node.is_root:
            return
        refresh_data = self.get_refresh_type(active_node)
        if refresh_data:
            self.get_connection_by_node(active_node).clear_by_type(
                refresh_data[0], refresh_data[1], refresh_data[2]
            )
            base_node = active_node.parent
            base_node.remove_children()
            base_node.collapse()
            tree.select_node(base_node)
        else:
            self.refresh_connection()

    def preview_data(self) -> None:
        tree: Tree = self.app.query_one(Tree)
        active_node: TreeNode = tree.cursor_node
        table_node: TreeNode = self.get_parent_node_by_type(active_node, [self.TABLE, self.VIEW])
        if table_node:
            table_name = self.strip_decorator(table_node.label.plain)
            schema_name = self.strip_decorator(
                self.get_schema_node(table_node).label.plain
            )
            self.get_connection_by_node(table_node).exec_preview(
                schema_name, table_name
            )

    def add_connection_node(self, connection: Connection):
        txt: Text = Text()
        txt.append(
            f"[{connection.env.name.upper()}] ",
            style=f"bold {self.get_env_color(connection.env)}",
        )
        txt.append(connection.id)
        self.tree.root.add(txt)
