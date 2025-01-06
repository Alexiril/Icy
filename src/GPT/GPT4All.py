""""""

from pathlib import Path
from typing import Iterable

# Don't have stubs for gpt4all
from gpt4all import GPT4All as _GPT4All  # type: ignore
from openai import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from src import State
from src.Interfaces import GPTInterface


class GPT4All(GPTInterface):
    """"""

    model: _GPT4All

    @staticmethod
    def gpt4all_model_loader(model_name: str) -> _GPT4All:
        # Auto downloading is something...
        return _GPT4All(model_name=model_name, model_path=Path(".") / ".models")

    def __init__(self) -> None:
        return

    def before_start(self, state: State) -> None:
        self.model = self.gpt4all_model_loader(state["settings"].get("gpt_model"))
        return

    def answer(
        self, request: str, state: State, system_prompt: str | None = None
    ) -> str | Iterable[str] | Stream[ChatCompletionChunk]:
        history = self.make_queue_copy_with_system_prompt(
            state, state["assistant-dialogue"], system_prompt
        )
        history.put({"role": "user", "content": request})

        def gpt_brakes(token_id: int, response: str) -> bool:
            return not state.get("__force_stop_stream", False)

        with self.model.chat_session(system_prompt):
            self.model._history = history.queue  # type: ignore
            return self.model.generate(
                request,
                max_tokens=2048,
                temp=1.0,
                streaming=True,
                callback=gpt_brakes,
            )
