import logging

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.dom import NoMatches
from textual.widgets import (
    Footer,
    Header,
    Label,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)
from textual.reactive import reactive
from textual.widget import Widget

from connections import Connection, Env
from connectors.connector import ConnectorType
from components.screens.quit_screen import QuitScreen
from components.screens.new_connection import NewConnectionScreen
from components.menu import Menu

logger = logging.getLogger(__name__)

CONNECTIONS = [
    Connection("First", "test", None, None, None, ConnectorType.SQLITE, Env.DEV),
    Connection("Second", "test", None, None, None, ConnectorType.SQLITE, Env.SIT),
    Connection("Third", "test", None, None, None, ConnectorType.SQLITE, Env.SAT),
    Connection("Fourth", "test", None, None, None, ConnectorType.SQLITE, Env.PROD),
]


class SiquelClient(App):
    CSS_PATH = "layout.tcss"
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("e", "exec_query", "Execute"),
        ("c", "clear_input", "Clear"),
        ("f", "format_query", "Format"),
        ("r", "refresh_parent", "Refresh parent"),
        ("R", "refresh_connection", "Refresh connection"),
        ("n", "request_new_connection", "New Connection"),
    ]
    SCHEMA = "[S]"
    TABLE = "[T]"
    VIEW = "[V]"
    SEQUENCE = "[Sq]"
    COLUMN = "[C]"

    active_panel = reactive(Widget, bindings=True)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if type(self.app.focused) is not Tree:
            if action in [
                "refresh_parent",
                "refresh_connection",
                "request_new_connection",
            ]:
                return False
        else:
            if action in ["clear_input", "exec_query"]:
                return False

        return True

    def __init__(self, connections: [Connection]):
        super().__init__()
        self.connections = connections

    menu: Menu

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="row box"):
                yield Header("Header")
            with Horizontal():
                with Vertical(classes="box column1"):
                    self.menu = Menu(self.connections)
                    yield self.menu.tree
                with TabbedContent(classes="box column4"):
                    with TabPane("Initial", id="initial"):
                        with Vertical():
                            with Horizontal(classes="box full_height"):
                                yield Label("Hello")
            with Horizontal(classes="row box"):
                yield Footer()

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        label: str = event.node.label.plain
        if label.startswith("["):
            self.menu.fill_child_nodes(event)
            conn: Connection = self.menu.get_connection_by_node(event.node)
            if conn:
                print(conn)
                logger.info(conn)
                self.add_connection_tab(conn)

    def get_connection_by_name(self, name: str) -> Connection:
        for connection in self.connections:
            if self.strip_decorator(name) == connection.id:
                return connection

    def strip_decorator(self, name: str) -> str:
        if name is None or not name.startswith("["):
            return name
        return name.split(" ")[1]

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

    def action_format_query(self) -> None:
        active_pane = self.app.query_one(TabbedContent).active_pane.id
        if active_pane == "initial":
            return
        conn: Connection = self.get_connection_by_name(active_pane)
        conn.format_query()

    def action_exec_query(self):
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)
        if tabbed_content.active_pane.id == "initial":
            return
        self.get_connection_by_name(tabbed_content.active_pane.id).exec_query()

    def action_refresh_connection(self) -> None:
        self.menu.refresh_connection()

    def action_refresh_parent(self) -> None:
        self.menu.refresh_parent()

    def action_request_quit(self) -> None:
        self.push_screen(QuitScreen())

    def action_request_new_connection(self) -> None:
        def result(conn: Connection | None):
            if conn:
                self.connections.append(conn)
                self.menu.add_connection_node(conn)

        self.push_screen(NewConnectionScreen(), result)

    def get_current_input(self) -> TextArea | None:
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)
        try:
            return tabbed_content.active_pane.query_one(TextArea)
        except NoMatches:
            return None


if __name__ == "__main__":
    app = SiquelClient(CONNECTIONS)
    app.run()
