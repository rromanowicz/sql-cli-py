
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Label,
)


class DeleteScreen(ModalScreen):
    """Delete confirmation screen."""

    def __init__(self, connection_name: str) -> None:
        self.connection_name = connection_name
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog quit container"):
            with Horizontal(classes="container w1"):
                yield Label(
                    f"Are you sure you want to delete '{self.connection_name}'?",
                    id="question",
                )
            with Horizontal(classes="container"):
                with Vertical(classes="w3"):
                    yield Button(
                        "Delete",
                        variant="error",
                        id="delete",
                        classes="dialog_button"
                    )
                with Vertical(classes="w3"):
                    yield Button(
                        "Cancel",
                        variant="primary",
                        id="cancel",
                        classes="dialog_button"
                    )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            self.dismiss(True)
        else:
            self.dismiss(False)
