import logging

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.dom import NoMatches
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)
from textual.widgets._tree import TreeNode

from connections import Connection, Env
from connectors.connector import ConnectorType

logger = logging.getLogger(__name__)

CONNECTIONS = [
    Connection("First", "test", None, None, None, ConnectorType.SqLite, Env.DEV),
    Connection("Second", "test", None, None, None, ConnectorType.SqLite, Env.SIT),
    Connection("Third", "test", None, None, None, ConnectorType.SqLite, Env.SAT),
    Connection("Fourth", "test", None, None, None, ConnectorType.SqLite, Env.PROD),
]


class SiquelClient(App):
    CSS_PATH = "layout.tcss"
    BINDINGS = [
        ("c", "clear_input", "Clear"),
        ("e", "exec_query", "Execute"),
        ("r", "refresh_parent", "Refresh parent"),
        ("R", "refresh_connection", "Refresh connection"),
        ("q", "request_quit", "Quit"),
    ]
    SCHEMA = "[S]"
    TABLE = "[T]"
    VIEW = "[V]"
    SEQUENCE = "[Sq]"
    COLUMN = "[C]"

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="row box"):
                yield Header("Header")
            with Horizontal():
                with Vertical(classes="box column1"):
                    yield self.menu()
                with TabbedContent(classes="box column4"):
                    with TabPane("Initial", id="initial"):
                        with Vertical():
                            with Horizontal(classes="box full_height"):
                                yield Label("Hello")
            with Horizontal(classes="row box"):
                yield Footer()

    def menu(self) -> Tree[str]:
        tree: Tree[str] = Tree("Connections")
        tree.root.expand()

        for connection in CONNECTIONS:
            txt: Text = Text()
            txt.append(
                f"[{connection.env.name.upper()}] ",
                style=f"bold {self.get_env_color(connection.env)}",
            )
            txt.append(connection.id)
            tree.root.add(txt)
        return tree

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        self.fill_child_nodes(event)

    def fill_child_nodes(self, event: Tree.NodeExpanded):
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
                    case self.TABLE | self.VIEW:
                        match prefix:
                            case self.TABLE:
                                type = "table"
                            case self.VIEW:
                                type = "view"
                        if parent_label[:3] == "[S]":
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
                            self.add_connection_tab(conn)
                            for schema_name in conn.schemas():
                                txt: Text = (
                                    Text()
                                    .append(f"{self.SCHEMA} ", style="turquoise2")
                                    .append(schema_name)
                                )
                                # event.node.add(f"[S] {schema_name}")
                                event.node.add(txt)

    def get_connection_by_node(self, node: TreeNode) -> Connection:
        base_name: str = self.get_base_node(node).label.plain
        return self.get_connection_by_name(base_name)

    def get_base_node(self, node: TreeNode) -> TreeNode:
        parent_node: TreeNode = node.parent
        if parent_node.is_root:
            return node
        else:
            return self.get_base_node(parent_node)

    def get_schema_node(self, node: TreeNode) -> TreeNode:
        if node.is_root:
            return None
        else:
            if node.label.plain.split(" ")[0] == self.SCHEMA:
                return node
            else:
                return self.get_schema_node(node.parent)

    def get_connection_by_name(self, name: str) -> Connection:
        for connection in CONNECTIONS:
            if self.strip_decorator(name) == connection.id:
                return connection

    def strip_decorator(self, name: str) -> str:
        if name is None or not name.startswith("["):
            return name
        return name.split(" ")[1]

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

    def input_area(self) -> TextArea:
        return TextArea.code_editor("SELECT * FROM DUAL;", language="sql")

    def add_connection_tab(self, conn: Connection):
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)

        try:
            tabbed_content.get_widget_by_id(conn.id)
        except NoMatches:
            pane = TabPane(conn.id, id=conn.id)
            input: Horizontal = Horizontal(
                conn.input, classes="half_height", id="input"
            )
            input.add_class(conn.env.name.lower())
            results: Horizontal = Horizontal(
                conn.results, classes="half_height", id="results"
            )
            results.add_class(conn.env.name.lower())

            pane._add_child(
                Vertical(
                    input,
                    results,
                ),
            )
            tabbed_content.add_pane(pane)
            tabbed_content.active = pane.id

    def on_mount(self) -> None:
        self.title = "Header Application"
        self.sub_title = "With title and sub-title"

    def action_clear_input(self) -> None:
        active_pane = self.app.query_one(TabbedContent).active_pane.id
        if active_pane == "initial":
            return
        conn: Connection = self.get_connection_by_name(active_pane)
        conn.input.clear()
        conn.results.clear()
        conn.results.columns.clear()

    def action_exec_query(self):
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)
        if tabbed_content.active_pane.id == "initial":
            return
        self.get_connection_by_name(tabbed_content.active_pane.id).exec_query()

    def action_refresh_connection(self) -> None:
        tree: Tree = self.app.query_one(Tree)
        active_node: TreeNode = tree.cursor_node
        if active_node is None or active_node.is_root:  # TODO: add root behaviour
            return
        self.get_connection_by_node(active_node).clear()
        base_node: TreeNode = self.get_base_node(active_node)
        base_node.remove_children()
        base_node.collapse()
        tree.select_node(base_node)

    def action_refresh_parent(self) -> None:
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
            self.action_refresh_connection()

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

    def get_current_input(self) -> TextArea | None:
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)
        try:
            return tabbed_content.active_pane.query_one(TextArea)
        except NoMatches:
            return None

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""
        self.push_screen(QuitScreen())


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()


if __name__ == "__main__":
    app = SiquelClient()
    app.run()
