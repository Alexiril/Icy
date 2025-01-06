""""""

from abc import ABCMeta, abstractmethod
from typing import Any

from src import State


class ActionInterface(metaclass=ABCMeta):
    """"""

    uid: str
    keys: list[str] = []

    language: dict[str, Any]

    @abstractmethod
    def __init__(self, state: State, language: dict[str, Any]) -> None:
        self.language = language

    @abstractmethod
    def __call__(
        self, state: State, words: list[str], *args: Any, **kwds: Any
    ) -> None: ...
