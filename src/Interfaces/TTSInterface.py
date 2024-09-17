""""""

from abc import ABCMeta, abstractmethod
from wave import Wave_read

from src.Interfaces.BasicInterface import BasicInterface


class TTSInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def generate_speech(self, data: str) -> Wave_read: ...
