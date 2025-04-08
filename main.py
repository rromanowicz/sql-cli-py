import logging
from rich.text import Text
from textual.app import App, ComposeResult
from textual.dom import NoMatches
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    Static,
    Tab,
    TabbedContent,
    TabPane,
    Tabs,
    TextArea,
    Tree,
)
from textual.widgets._tree import TreeNode
from connections import Connection, Env

logger = logging.getLogger(__name__)

ROWS = [
    ("lane", "swimmer", "country", "time"),
    (4, "Joseph Schooling", "Singapore", 50.39),
    (2, "Michael Phelps", "United States", 51.14),
    (5, "Chad le Clos", "South Africa", 51.14),
    (6, "László Cseh", "Hungary", 51.14),
    (3, "Li Zhuhao", "China", 51.26),
    (8, "Mehdy Metella", "France", 51.58),
    (7, "Tom Shields", "United States", 51.73),
    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
    (10, "Darren Burns", "Scotland", 51.84),
]

CONNECTIONS = [
    Connection("First", Env.DEV),
    Connection("Second", Env.SIT),
]


class GridLayoutExample(App):
    CSS_PATH = "layout.tcss"
    BINDINGS = [("c", "clear_input", "Clear")]

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
                    with TabPane("Test", id="test"):
                        with Vertical():
                            with Horizontal(classes="box half_height"):
                                yield self.input_area()
                            with Horizontal(classes="box half_height"):
                                yield self.results()
            with Horizontal(classes="row box"):
                yield Footer()

    def menu(self) -> Tree[str]:
        tree: Tree[str] = Tree("Connections")
        tree.root.expand()

        for connection in CONNECTIONS:
            tree.root.add(connection.id)
        return tree

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        label: str = event.node.label.plain
        if label.startswith("["):
            match label[1]:
                case "S":
                    for table_name in self.get_connection_by_name(
                        event.node.parent.label.plain
                    ).tables(label[4:]):
                        event.node.add(f"[T] {table_name}")
                case "T":
                    for column_def in self.get_connection_by_name(
                        event.node.parent.parent.label.plain
                    ).columns(event.node.parent.label.plain[4:], label[4:]):
                        column = event.node.add(f"[C] {column_def[0]}")
                        column.add_leaf(column_def[1])
                        if column_def[2]:
                            column.add_leaf("NOT NULL")
        elif event.node.parent is not None and event.node.parent.is_root:
            for schema_name in self.get_connection_by_name(
                event.node.label.plain
            ).schemas():
                event.node.add(f"[S] {schema_name}")

    def get_connection_by_node(self, node: TreeNode) -> Connection:
        base_name: str = self.get_base_node(node).label.plain
        return self.get_connection_by_name(base_name)

    def get_base_node(self, node: TreeNode) -> TreeNode:
        if node.label.plain.startswith("["):
            self.get_base_node(node.parent)
        else:
            return node

    def get_connection_by_name(self, name: str) -> Connection:
        for connection in CONNECTIONS:
            if name == connection.id:
                return connection

    def input_area(self) -> TextArea:
        return TextArea.code_editor("SELECT * FROM DUAL;", language="sql")

    def tabs(self) -> None:
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)
        for conn in CONNECTIONS:
            pane = TabPane(conn.id)
            pane._add_child(
                Vertical(
                    Horizontal(conn.input, classes="box half_height", id="input"),
                    Horizontal(conn.results, classes="box half_height", id="results"),
                ),
            )
            tabbed_content.add_pane(pane)

    def results(self) -> DataTable:
        table = DataTable()
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])
        return table

    def on_mount(self) -> None:
        self.title = "Header Application"
        self.sub_title = "With title and sub-title"
        self.tabs()

    def action_clear_input(self) -> None:
        input = self.get_current_input()
        if input:
            input.text = ""

    def get_current_input(self) -> TextArea | None:
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)
        try:
            return tabbed_content.active_pane.query_one(TextArea)
        except NoMatches:
            return None


if __name__ == "__main__":
    app = GridLayoutExample()
    app.run()
