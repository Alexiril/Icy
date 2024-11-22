""""""

from json import dumps
from pathlib import Path
from typing import Any

from src import Node, State


class PrevDataWriter(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "Previous data file writer", left, right, [("settings", dict[str, Any])]
        )

    def __call__(self, state: State) -> None:
        prev_data_file: Path = Path(".") / "prev.data"
        initial_file: bytes = b""
        try:
            if prev_data_file.is_file():
                with open(prev_data_file, "rb") as original_file:
                    initial_file = original_file.read()
            with open(prev_data_file, "wt") as file:
                file.write(dumps(state["settings"]))
        except (OSError, TypeError) as e:
            self.log_info(f"Couldn't save the prev.data file due to {e}.")
            if len(initial_file) == 0:
                return
            self.log_info("Attempting to write original prev.data file data back.")
            try:
                with open(prev_data_file, "wb") as file:
                    file.write(initial_file)
            except OSError as e:
                self.log_error(e)
        return
