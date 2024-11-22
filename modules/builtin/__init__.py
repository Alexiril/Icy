""""""

from typing import Any
from src import State
from src.Interfaces import ModuleInterface, ActionInterface

from modules.builtin.actions import QuitAction, TestAction2


class Module(ModuleInterface):
    """"""

    def __init__(self, module_info: dict[str, Any]) -> None:
        return

    def get_actions(self, state: State) -> list[ActionInterface]:
        return [
            QuitAction(),
            TestAction2(),
        ]
