""""""

from abc import ABCMeta, abstractmethod
from typing import Any

from src import State


class ActionInterface(metaclass=ABCMeta):
    """"""

    uid: str
    keys: list[str] = []

    @abstractmethod
    def __call__(
        self, state: State, words: list[str], *args: Any, **kwds: Any
    ) -> None: ...
