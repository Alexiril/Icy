""""""

from abc import ABCMeta, abstractmethod

from src.Interfaces.BasicInterface import BasicInterface


class STTInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    samplerate: int

    @abstractmethod
    def recognize(self, data: bytes) -> str: ...
