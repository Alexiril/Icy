""""""

from abc import ABCMeta, abstractmethod

from src.Interfaces.BasicInterface import BasicInterface


class PhraseProcessorInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def process(self, phrase: str) -> str: ...
