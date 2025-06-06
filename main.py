import logging

from cryptography.fernet import InvalidToken
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.dom import NoMatches
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Header,
    Label,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)

import util.bindings as B
import util.conn_file as F
from components.menu import Menu
from components.screens.edit_connection import EditConnectionScreen
from components.screens.new_connection import NewConnectionScreen
from components.screens.quit_screen import QuitScreen
from connection.connection import Connection
from util.crypto import load_env

logger = logging.getLogger(__name__)


class SiquelClient(App):
    CSS_PATH = "layout.tcss"
    BINDINGS = B.ALL_BINDINGS

    active_panel = reactive(Widget, bindings=True)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if type(self.app.focused) is not Tree:
            if action in B.actions(B.CONNECTION_TREE_BINDINGS):
                return False
        else:
            if action in B.actions(B.QUERY_BINDINGS):
                return False

        return True

    def __init__(self):
        super().__init__()
        try:
            self.connections = F.read_conn_file()
        except InvalidToken:
            self.connections = []

    menu: Menu

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="row box"):
                yield Header("Header")
            with Horizontal():
                with Vertical(classes="box column1", id="menu-container"):
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
            # try:
            self.menu.fill_child_nodes(event)
            conn: Connection = self.menu.get_connection_by_node(event.node)
            if conn:
                print(conn)
                logger.info(conn)
                self.add_connection_tab(conn)
            # except Exception as e:
            #     self.app.action_notify(
            #         f"{e}", title=f"{e.__class__.__name__}", severity="error"
            #     )
            #     event.node.collapse()

    def get_connection_by_id(self, name: str) -> Connection:
        for connection in self.connections:
            if self.strip_decorator(name) == connection.id:
                return connection

    def strip_decorator(self, name: str) -> str:
        if name is None or not name.startswith("["):
            return name
        return name.split(" ")[1]

    def input_area(self) -> TextArea:
        return TextArea.code_editor("SELECT * FROM DUAL;", language="sql")

    def add_connection_tab(self, connection: Connection):
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)

        try:
            tabbed_content.get_widget_by_id(connection.id)
        except NoMatches:
            pane = TabPane(connection.conn.display_name(), id=connection.id)
            input: Horizontal = Horizontal(
                connection.input, classes="half_height", id="input"
            )
            input.add_class(connection.conn.env.name.lower())
            results: Horizontal = Horizontal(
                connection.results, classes="half_height", id="results"
            )
            results.add_class(connection.conn.env.name.lower())

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
        conn: Connection = self.get_connection_by_id(active_pane)
        conn.input.clear()
        conn.results.clear()
        conn.results.columns.clear()

    def action_format_query(self) -> None:
        active_pane = self.app.query_one(TabbedContent).active_pane.id
        if active_pane == "initial":
            return
        conn: Connection = self.get_connection_by_id(active_pane)
        conn.format_query()

    def action_exec_query(self):
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)
        if tabbed_content.active_pane.id == "initial":
            return
        self.get_connection_by_id(tabbed_content.active_pane.id).exec_query()

    def action_preview_data(self) -> None:
        self.menu.preview_data()

    def action_refresh_connection(self) -> None:
        self.menu.refresh_connection()

    def action_refresh_parent(self) -> None:
        self.menu.refresh_parent()

    def action_request_quit(self) -> None:
        self.push_screen(QuitScreen())

    def action_request_new_connection(self) -> None:
        existing_connections: [(str, str)] = list(
            map(lambda c: tuple([c.conn.env.name, c.id]), self.connections)
        )

        def result(conn: Connection | None):
            if conn:
                self.connections.append(conn)
                self.menu.add_connection_node(conn)

        self.push_screen(NewConnectionScreen(existing_connections), result)

    def action_edit_connection(self) -> None:
        connection: Connection = self.menu.get_selected_connection()
        if connection:
            existing_connections: [(str, str)] = list(
                map(lambda c: tuple([c.conn.env.name, c.conn.id]), self.connections)
            )
            existing_connections.remove(
                tuple([connection.conn.env.name, connection.conn.id])
            )

            def result(conn: Connection | None):
                if conn:
                    self.update_connection(self.connections.index(connection), conn)

            self.push_screen(
                EditConnectionScreen(existing_connections, connection.conn), result
            )

    def action_save_connections(self) -> None:
        F.write_conn_file(self.connections)
        self.app.action_notify(f"Saved {len(self.connections)} connections", "Saved")

    def action_tree_left(self) -> None:
        self.menu.tree.action_cursor_parent()

    def action_tree_down(self) -> None:
        self.menu.tree.action_cursor_down()

    def action_tree_up(self) -> None:
        self.menu.tree.action_cursor_up()

    def action_tree_right(self) -> None:
        self.menu.tree.action_select_cursor()

    def get_current_input(self) -> TextArea | None:
        tabbed_content: TabbedContent = self.app.query_one(TabbedContent)
        try:
            return tabbed_content.active_pane.query_one(TextArea)
        except NoMatches:
            return None

    def update_connection(self, idx: int, connection: Connection) -> None:
        self.connections[idx].conn = connection.conn
        self.connections[idx].conn.connector().clear()
        self.menu.refresh_tree(self.connections)


if __name__ == "__main__":
    load_env()
    app = SiquelClient()
    app.run()
