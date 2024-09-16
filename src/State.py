""""""

from typing import Any, TYPE_CHECKING

from src.StatePhase import StatePhase

if TYPE_CHECKING:
    from src.Node import Node


class State(dict[str, Any]):
    """"""

    phase: StatePhase
    stack: list["Node"]

    def __str__(self) -> str:
        options = "\n".join(
            [x + " : " + getattr(self, x) for x in dir(self) if not x.startswith("_")]
        )
        return f"State {{\n{options}\n}}"
