""""""

from abc import ABCMeta, abstractmethod
from typing import Any

from src import State
from src.Interfaces.ActionInterface import ActionInterface


class ModuleInterface(metaclass=ABCMeta):
    """"""

    @abstractmethod
    def __init__(self, module_info: dict[str, Any]) -> None: ...

    @abstractmethod
    def get_actions(self, state: State) -> list[ActionInterface]: ...
