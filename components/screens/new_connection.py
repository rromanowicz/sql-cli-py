from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select

from connection.conn import Conn
from connection.connection import Connection
from connectors.connector import ConnectorType
from connectors.exceptions import NewConnectionError
from util.model import Env


class NewConnectionScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog new_conn container"):
            with Horizontal(classes="container w1"):
                yield Label("Add new connection", id="header")

            with Horizontal(classes="container w1"):
                with Vertical(classes="w7"):
                    yield Input(placeholder="Name", id="name")
                with Vertical(classes="w3"):
                    yield Select(
                        ((line, line) for line in Env.list()),
                        allow_blank=False,
                        id="env",
                    )
            with Horizontal(classes="container w1"):
                with Vertical(classes="w5"):
                    yield Input(placeholder="User", id="user")
                with Vertical(classes="w5"):
                    yield Input(placeholder="Password", id="password", password=True)

            with Horizontal(classes="container w1"):
                with Vertical(classes="w7"):
                    yield Input(placeholder="Database", id="database")
                with Vertical(classes="w3"):
                    yield Select(
                        ((line, line) for line in ConnectorType.list()),
                        allow_blank=False,
                        id="connectionType",
                    )

            with Horizontal(classes="container w1"):
                with Vertical(classes="w7"):
                    yield Input(placeholder="Host", id="host")
                with Vertical(classes="w3"):
                    yield Input(placeholder="Port", id="port")

            with Horizontal(classes="container padded"):
                with Vertical(classes="w3"):
                    yield Button(
                        "Add", variant="primary", id="confirm", classes="dialog_button"
                    )
                with Vertical(classes="w3"):
                    yield Button(
                        "Cancel",
                        variant="error",
                        id="cancel",
                        classes="dialog_button",
                    )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            name: str = none_if_empty(self.query_one("#name").value)
            env: str = none_if_empty(self.query_one("#env").value)
            db: str = none_if_empty(self.query_one("#database").value)
            user: str = none_if_empty(self.query_one("#user").value)
            password: str = none_if_empty(self.query_one("#password").value)
            host: str = none_if_empty(self.query_one("#host").value)
            port: str = none_if_empty(self.query_one("#port").value)
            connectionType: str = self.query_one("#connectionType").value
            port_int = None if port is None or len(port) == 0 else int(port)

            try:
                conn: Conn = Conn(
                    name,
                    db,
                    host,
                    port_int,
                    user,
                    password,
                    ConnectorType[connectionType.upper()],
                    Env[env],
                )
                connection = Connection.from_conn(conn)
                connection.test()

                self.dismiss(connection)
            except NewConnectionError as e:
                self.app.action_notify(
                    f"{e}", title=f"{e.__class__.__name__}", severity="error"
                )
        else:
            self.app.pop_screen()

def none_if_empty(input: str) -> str | None:
    if input is None or len(input) == 0:
        return None
    else:
        return input
