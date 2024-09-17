""""""

from abc import ABCMeta, abstractmethod
from queue import Queue
from typing import Iterable

from openai import Stream
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from src.Interfaces.BasicInterface import BasicInterface


class GPTInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @abstractmethod
    def answer(
        self, messages: Queue[ChatCompletionMessageParam]
    ) -> str | Iterable[str] | Stream[ChatCompletionChunk]: ...
