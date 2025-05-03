from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select

from connection.conn import Conn
from connection.connection import Connection
from connectors.connector import ConnectorType
from connectors.exceptions import NewConnectionError
from util.model import Env


class EditConnectionScreen(ModalScreen):
    def __init__(self, existing_connections: [(str, str)], conn: Conn):
        self.existing_connections = existing_connections
        self.conn = conn
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog new_conn container"):
            with Horizontal(classes="container w1"):
                yield Label("Add new connection", id="header")

            with Horizontal(classes="container w1"):
                with Vertical(classes="w7"):
                    yield Input(placeholder="Name", id="name", value=self.conn.id)
                with Vertical(classes="w3"):
                    yield Select(
                        ((line, line) for line in Env.list()),
                        allow_blank=False,
                        id="env",
                        value=self.conn.env.value,
                    )
            with Horizontal(classes="container w1"):
                with Vertical(classes="w5"):
                    yield Input(placeholder="User", id="user", value=self.conn.user)
                with Vertical(classes="w5"):
                    yield Input(
                        placeholder="Password",
                        id="password",
                        password=True,
                        value=self.conn.passwd,
                    )

            with Horizontal(classes="container w1"):
                with Vertical(classes="w7"):
                    yield Input(
                        placeholder="Database", id="database", value=self.conn.database
                    )
                with Vertical(classes="w3"):
                    yield Select(
                        ((line, line) for line in ConnectorType.list()),
                        allow_blank=False,
                        id="connectionType",
                        value=self.conn.connector_type.value
                    )

            with Horizontal(classes="container w1"):
                with Vertical(classes="w7"):
                    yield Input(placeholder="Host", id="host", value=self.conn.host)
                with Vertical(classes="w3"):
                    yield Input(placeholder="Port", id="port", value=str(self.conn.port))

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
                for connection in self.existing_connections:
                    if name == connection[1] and env == connection[0]:
                        raise NewConnectionError(
                            f"Connection '\[{env}] {name}]' already exists"
                        )
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
