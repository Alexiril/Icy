from typing import TYPE_CHECKING, Any

from assistant_function import AssistantFunction

if TYPE_CHECKING:
    from appstate import AppState


class ModuleInterface:

    def __init__(self, state: "AppState") -> None:
        self.state = state
        self.module_config: dict[str, Any] = {}

    def get_function(self) -> AssistantFunction:
        return AssistantFunction([], None)
