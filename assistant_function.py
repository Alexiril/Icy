from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from appstate import AppState


class AssistantFunction:

    class StateFunction(Protocol):

        def __call__(self, state: "AppState", *args: Any, **kwds: Any) -> None: ...

    keys: list[str] = []
    reaction: StateFunction | None = None

    def __init__(self, keys: list[str], reaction: StateFunction | None) -> None:
        self.keys = keys
        self.reaction = reaction
