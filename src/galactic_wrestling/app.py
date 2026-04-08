from __future__ import annotations

from textual.app import App

from galactic_wrestling.ai_opponents import ensure_ai_opponents
from galactic_wrestling.config import ensure_data_tree
from galactic_wrestling.ui.screens import LoginScreen


class GalacticApp(App[None]):
    """Root application: strict login, then menus."""

    TITLE = "Galactic Wrestling"
    SUB_TITLE = "Deckbuilder"

    player_id: str | None = None
    login_name: str | None = None

    def on_mount(self) -> None:
        ensure_data_tree()
        ensure_ai_opponents()
        self.push_screen(LoginScreen())


def main() -> None:
    GalacticApp().run()


if __name__ == "__main__":  # pragma: no cover
    main()
