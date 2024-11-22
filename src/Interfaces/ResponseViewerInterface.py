""""""

from abc import ABCMeta, abstractmethod
from typing import Callable

from src.Interfaces.BasicInterface import BasicInterface


class ResponseViewerInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def view(self, text: str) -> None: ...

    @abstractmethod
    def hook(self, get_text: Callable[[], str]) -> None: ...

    @abstractmethod
    def review(self) -> None: ...

    @abstractmethod
    def finished(self) -> bool: ...

    @abstractmethod
    def normal_terminate(self) -> None: ...
