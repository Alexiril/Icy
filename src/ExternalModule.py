""""""

from types import ModuleType
from typing import Any

from src.Interfaces import ModuleInterface
from src.State import State


class ExternalModule:
    """"""

    module_name: str
    module_version: str
    module_info: dict[str, Any]

    actual_module: ModuleInterface

    def __init__(
        self,
        module_info: dict[str, Any],
        actual_module: ModuleType,
    ) -> None:
        self.module_name = module_info.get("name", "Unnamed module")
        self.module_version = module_info.get("version", "No version")
        self.module_info = module_info

        if not hasattr(actual_module, "Module") or not issubclass(
            getattr(actual_module, "Module"), ModuleInterface
        ):
            raise RuntimeError(f"The module '{self.module_name}'")
        self.actual_module = getattr(actual_module, "Module")(self.module_info)

    def __call__(self, state: State) -> None:
        self.actual_module(state)
        return
