""""""

from queue import Queue
from typing import Any

from openai.types.chat import ChatCompletionMessageParam

from src import Node, State
from src.Functions import stream_to_str


class GPTDialogueSaver(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "GPT dialog saver",
            left,
            right,
            [
                ("translations", dict[str, dict[str, str]]),
                ("assistant-dialogue", Queue[ChatCompletionMessageParam]),
                ("settings", dict[str, Any]),
            ],
        )

    def __call__(self, state: State) -> None:
        system_prompt = state["translations"][""][
            "Your only task is to summarize the conversation to reduce it into the "
            "smallest possible number of sentences."
        ]
        prev = state["settings"].get("gpt_info")
        if len(prev) > 1:
            request = state["translations"][""][
                "From previous conversation you know this information:"
            ] + f' {prev}'
        else:
            request = system_prompt
        summary = stream_to_str(
            state,
            state["gpt-interface"].answer(request, state, system_prompt),
        )
        state["settings"]["gpt_info"] = summary
        return
