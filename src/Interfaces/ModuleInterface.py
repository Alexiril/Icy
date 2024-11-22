""""""

from abc import ABCMeta, abstractmethod
from typing import Any

from src import State


class ModuleInterface(metaclass=ABCMeta):
    """"""

    module_info: dict[str, Any]

    def __init__(self, module_info: dict[str, Any]) -> None:
        self.module_info = module_info

    @abstractmethod
    def __call__(self, state: State) -> None: ...
