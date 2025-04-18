from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label, Input, Select
from connections import Connection, Env
from connectors.connector import ConnectorType


class NewConnectionScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog new_conn container"):
            with Horizontal(classes="container w1"):
                yield Label(
                    "Add new connection",
                )

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
                    yield Input(placeholder="Password", id="password")

            with Horizontal(classes="container w1"):
                with Vertical(classes="w7"):
                    yield Input(placeholder="Database", id="database")
                with Vertical(classes="w3"):
                    yield Select(
                        ((line, line) for line in ConnectorType.list()),
                        allow_blank=False,
                        id="env",
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
            name: str = self.query_one("#name").value
            env: str = self.query_one("#env").value
            db: str = self.query_one("#database").value
            user: str = self.query_one("#user").value
            password: str = self.query_one("#password").value
            host: str = self.query_one("#host").value
            # port: str = self.query_one("#port").value

            conn: Connection = Connection(
                name, db, host, user, password, ConnectorType.SQLITE, Env[env]
            )

            self.dismiss(conn)
        else:
            self.app.pop_screen()
