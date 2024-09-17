""""""

from abc import ABCMeta, abstractmethod

from src.Interfaces.BasicInterface import BasicInterface


class STTInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def recognize(self, data: bytes) -> str: ...
