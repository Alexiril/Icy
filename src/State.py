""""""

from typing import Any, TYPE_CHECKING

from src.StatePhase import StatePhase

if TYPE_CHECKING:
    from src.Node import Node


class State(dict[str, Any]):
    """"""

    phase: StatePhase = StatePhase.frozen
    stack: list["Node"] = []

    def __str__(self) -> str:
        options = f"Phase : {self.phase}\nStack : {self.stack}\n"
        options = "\n".join(
            [f"{key} : {value}" for key, value in self.items()]
        )
        return f"State {{\n{options}\n}}"
