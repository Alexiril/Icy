""""""

from types import ModuleType
from typing import Any


class ExternalModule:
    """"""

    module_name: str
    module_version: str
    module_info: dict[str, Any]

    actual_module: ModuleType

    def __init__(
        self,
        module_info: dict[str, Any],
        actual_module: ModuleType,
    ) -> None:
        self.module_name = module_info.get("name", "Unnamed module")
        self.module_version = module_info.get("version", "No version")
        self.module_info = module_info

        self.actual_module = actual_module
