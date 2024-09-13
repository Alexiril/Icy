"""This module contains an AssistantFunction class. An Assistant instance uses
it to store and execute functions, the assistant is able to run."""

from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from appstate import AppState


class AssistantFunction:
    """Contains keyphrases which should be said by a user to run the reaction
    (any callable)."""

    class StateFunction(Protocol):
        """Protocol for all reactions in assistant functions."""

        def __call__(self, state: "AppState", *args: Any, **kwds: Any) -> None: ...

    keys: list[str] = []
    reaction: StateFunction | None = None

    def __init__(self, keys: list[str], reaction: StateFunction | None) -> None:
        self.keys = keys
        self.reaction = reaction
