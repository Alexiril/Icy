""""""

from typing import Any, Protocol

from src.State import State

class AssistantAction:
    """"""

    class StateFunction(Protocol):

        def __call__(self, state: State, *args: Any, **kwds: Any) -> None: ...

    keys: list[str] = []
    reaction: StateFunction | None = None

    def __init__(self, keys: list[str], reaction: StateFunction | None) -> None:
        self.keys = keys
        self.reaction = reaction
