""""""

from typing import Any

from src import Node, State, save_prev


class PrevDataWriter(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "Previous data file writer", left, right, [("settings", dict[str, Any])]
        )

    def __call__(self, state: State) -> None:
        try:
            save_prev(state["settings"])
        except Exception as e:
            self.log_error(e)
