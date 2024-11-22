""""""

from abc import ABCMeta, abstractmethod
from typing import Iterable

from openai import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from src import State
from src.Interfaces.BasicInterface import BasicInterface


class GPTInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def answer(
        self, request: str, state: State
    ) -> str | Iterable[str] | Stream[ChatCompletionChunk]: ...
