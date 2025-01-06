""""""

from abc import ABCMeta, abstractmethod
from queue import Queue
from typing import Any, Iterable

from openai import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

from src import State
from src.Interfaces.BasicInterface import BasicInterface


class GPTInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    @staticmethod
    def make_queue_copy_with_system_prompt(
        state: State, history: Queue[dict[str, Any]], system_prompt: str | None = None
    ) -> Queue[dict[str, Any]]:
        bot_name_description = state["translations"][""][
            "You are a nice friend, not just an assistant, your name is"
        ]
        final_command = state["translations"][""][
            "Answer creative and detailed, but short."
        ]
        gender = state["settings"].get("assistant_gender")
        gpt_info = state["settings"].get("gpt_info")
        gpt_info_pre = state["translations"][""]["You know that:"]
        result: Queue[dict[str, Any]] = Queue()
        result.put(
            {
                "role": "system",
                "content": (
                    (
                        f'{bot_name_description} '
                        f'{state["settings"].get("assistant_name")}. '
                        f'{state["translations"][""]["Your gender is "]} '
                        f'{state["translations"][""][gender]}. '
                        f'{final_command} '
                        f'{gpt_info_pre if len(gpt_info) != 0 else ""} {gpt_info}'
                    )
                    if system_prompt is None
                    else system_prompt
                ),
            }
        )
        for i in history.queue:
            result.put(i)
        return result

    @abstractmethod
    def answer(
        self, request: str, state: State, system_prompt: str | None = None
    ) -> str | Iterable[str] | Stream[ChatCompletionChunk]: ...
