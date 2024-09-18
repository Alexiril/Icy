""""""

from abc import ABCMeta, abstractmethod

from src.Interfaces.BasicInterface import BasicInterface


class AudioProcessorInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def process(self, data: bytes) -> bytes: ...
