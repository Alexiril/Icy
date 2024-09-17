""""""

from json import JSONDecodeError, loads
from pathlib import Path
from typing import Any

from src import Node, State


class PrevDataReader(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__("Previous data file reader", left, right)

    def __call__(self, state: State) -> None:
        settings: dict[str, Any] = {}
        prev_data_file: Path = Path(".") / "prev.data"
        if prev_data_file.is_file():
            try:
                with open(prev_data_file, "rb") as file:
                    settings = loads(file.read())
            except (OSError, JSONDecodeError) as e:
                self.log_error(e)
        if "settings" not in state:
            state["settings"] = {}
        state["settings"].update(settings)
        return
