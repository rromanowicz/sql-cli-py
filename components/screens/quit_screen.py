from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Label,
)


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog quit container"):
            with Horizontal(classes="container w1"):
                yield Label(
                    "Are you sure you want to quit?",
                    id="question",
                )
            with Horizontal(classes="container"):
                with Vertical(classes="w3"):
                    yield Button(
                        "Quit",
                        variant="error",
                        id="quit",
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
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()
