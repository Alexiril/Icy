""""""

from pathlib import Path
from typing import Iterable

# Don't have stubs for gpt4all
from gpt4all import GPT4All as _GPT4All  # type: ignore
from openai import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk  # type: ignore

from src import State
from src.Interfaces import GPTInterface


class GPT4All(GPTInterface):
    """"""

    @staticmethod
    def gpt4all_model_loader(model_name: str) -> _GPT4All:
        # Auto downloading is something...
        return _GPT4All(model_name=model_name, model_path=Path(".") / ".models")

    def __init__(self) -> None:
        return

    def before_start(self, state: State) -> None:
        return

    def answer(
        self, request: str, state: State
    ) -> str | Iterable[str] | Stream[ChatCompletionChunk]:
        raise NotImplementedError
