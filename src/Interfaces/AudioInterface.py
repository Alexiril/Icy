""""""

from abc import ABCMeta, abstractmethod
from wave import Wave_read

from src.Interfaces.BasicInterface import BasicInterface


class AudioInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def output(self, data: Wave_read) -> None: ...

    @abstractmethod
    def input(self) -> bytes: ...
