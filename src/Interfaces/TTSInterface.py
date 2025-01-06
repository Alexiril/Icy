""""""

from abc import ABCMeta, abstractmethod
from wave import Wave_read
from re import MULTILINE, compile as re_compile, search

from src.Interfaces.BasicInterface import BasicInterface


class TTSInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @staticmethod
    def remove_unreadable(text: str) -> str:
        text = text.replace("*", "").replace("#", "")
        pattern = re_compile(r"^```(?:.+)\n([\s\S]*?)```$", MULTILINE)
        while (match := search(pattern, text)) is not None:
            text = text[: match.start(0)] + text[match.end(0) :]
        return text

    @abstractmethod
    def generate_speech(self, data: str) -> Wave_read: ...
