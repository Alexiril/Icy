""""""

from openai.types.chat import ChatCompletionMessageParam
from queue import Queue
from src import Node, State


class GPTDialogueHook(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "GPT dialog hook",
            left,
            right,
            [
                ("assistant-dialogue", Queue[ChatCompletionMessageParam]),
                ("response", object),
            ],
        )

    def __call__(self, state: State) -> None:
        if "gpt-answered" not in state:
            return
        if not isinstance(gpt := state["gpt-answered"], bool):
            self.log_error(
                RuntimeWarning(
                    "Incorrect type of 'gpt-answered' parameter "
                    f"passed: [{type(gpt)}]."
                )
            )
            return
        if gpt:
            if not isinstance(response := state["response"], str):
                self.log_error(
                    RuntimeWarning(
                        "Incorrect type of 'response' parameter "
                        f"passed: [{type(response)}]."
                    )
                )
                return
            state["assistant-dialogue"].put(
                {
                    "role": "assistant",
                    "content": state["response"],
                }
            )
        return
