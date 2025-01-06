""""""

from typing import Any
from src import State
from src.Interfaces import ModuleInterface, ActionInterface

from modules.os.actions import OpenApplicationAction


class Module(ModuleInterface):
    """"""

    def __init__(
        self, module_info: dict[str, Any], translations: dict[str, dict[str, Any]]
    ) -> None:
        super().__init__(module_info, translations)

    def get_actions(self, state: State) -> list[ActionInterface]:
        return [
            OpenApplicationAction(
                state, self.translations[state["translations"][""]["lang_name"]]
            ),
        ]
