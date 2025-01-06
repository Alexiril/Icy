""""""

from typing import Iterable
from openai import APIStatusError, OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from termcolor import colored
from src import State
from src.GPT.GPT4All import GPT4All
from src.Interfaces import GPTInterface


class OpenAIGPT(GPTInterface):
    """"""

    reserve_interface: GPTInterface = GPT4All()

    def __init__(self) -> None:
        return

    def before_start(self, state: State) -> None:
        self.reserve_interface.before_start(state)
        return

    def answer(
        self, request: str, state: State, system_prompt: str | None = None
    ) -> str | Iterable[str] | Stream[ChatCompletionChunk]:
        history = self.make_queue_copy_with_system_prompt(
            state, state["assistant-dialogue"], system_prompt
        )
        history.put({"role": "user", "content": request})
        try:
            return OpenAI().chat.completions.create(
                model="gpt-4o-mini",
                messages=list(history.queue),
                temperature=1,
                stream=True,
            )
        except APIStatusError as e:
            print(colored(f"OpenAI services are unavaliable: {e}.", "light_red"))
        except Exception as e:
            print(
                colored(
                    f"Exception while running OpenAI GPT request: {e}.", "light_red"
                )
            )
        return self.reserve_interface.answer(request, state, system_prompt)
