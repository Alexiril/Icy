""""""

from abc import ABCMeta, abstractmethod
from typing import Callable

from src import State
from src.Interfaces.BasicInterface import BasicInterface


class ResponseViewerInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def view(self, text: str) -> None: ...

    @abstractmethod
    def hook(
        self, state: State, get_text: Callable[[], str], is_finished: Callable[[], bool]
    ) -> None: ...

    @abstractmethod
    def review(self) -> None: ...
