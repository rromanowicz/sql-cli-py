import logging
from rich.text import Text
from textual.app import App, ComposeResult
from textual.dom import NoMatches
from textual.containers import Horizontal, Vertical
from textual.widgets import (
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
    BINDINGS = [("c", "clear_input", "Clear"), ("e", "exec_query", "Execute")]

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
                conn: Connection = self.get_connection_by_node(event.node)
                match label[:3]:
                    case "[S]":
                        for table_name in conn.tables(self.strip_decorator(label)):
                            event.node.add(
                                Text()
                                .append("[T] ", style="turquoise2")
                                .append(table_name)
                            )
                    case "[T]":
                        for column_def in conn.columns(
                            self.strip_decorator(event.node.parent.label.plain),
                            self.strip_decorator(label),
                        ):
                            txt: Text = (
                                Text()
                                .append("[C] ", style="turquoise2")
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
                                    .append("[S] ", style="turquoise2")
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

    def get_connection_by_name(self, name: str) -> Connection:
        for connection in CONNECTIONS:
            if self.strip_decorator(name) == connection.id:
                return connection

    def strip_decorator(self, name: str) -> str:
        idx: int = name.find("] ")
        if idx == -1:
            return name
        return name[idx + 2 :]

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
        pane = TabPane(conn.id, id=conn.id)
        input: Horizontal = Horizontal(conn.input, classes="half_height", id="input")
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

    def get_current_input(self) -> TextArea | None:
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)
        try:
            return tabbed_content.active_pane.query_one(TextArea)
        except NoMatches:
            return None


if __name__ == "__main__":
    app = SiquelClient()
    app.run()
