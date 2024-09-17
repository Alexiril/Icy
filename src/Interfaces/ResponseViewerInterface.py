""""""

from abc import ABCMeta, abstractmethod

from src.Interfaces.BasicInterface import BasicInterface


class ResponseViewerInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def view(self, text: str) -> None: ...
