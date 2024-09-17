""""""

from typing import Any, Iterable

from openai import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from termcolor import colored

from src import Node, State
from src.Interfaces import ResponseViewerInterface


class AssistantResponse(Node):
    """"""

    viewers: Iterable[ResponseViewerInterface]

    def __init__(
        self,
        left: Node | None,
        right: Node | None,
        viewers: Iterable[ResponseViewerInterface],
    ) -> None:
        self.viewers = viewers
        super().__init__(
            "Assistant response node",
            left,
            right,
            [
                ("settings", dict[str, Any]),
                ("response", str | Iterable[str] | Stream[ChatCompletionChunk])
            ],
        )

    def __call__(self, state: State) -> None:
        response: str | Iterable[str] | Stream[ChatCompletionChunk] = state["response"]
        if type(response) is str:
            print(colored(response, "cyan"))
            for viewer in self.viewers:
                viewer.view(response)
        else:
            punctuation = ".;!?:"
            result_string = ""

            def update_text() -> str:
                return result_string

            finished: bool = False
            MessageWindow(
                text=update_text,
                show=lambda: not finished,
                speak_worker=self.speak_worker,
            )

            def punctuation_rfind(s: str) -> int:
                index = len(s) - 1
                for symbol in s[::-1]:
                    if symbol in punctuation:
                        return index
                    index -= 1
                return -1

            def handle_part(text: str) -> None:
                nonlocal result_string
                result_string += text
                if text not in punctuation:
                    self.generate_speech(text)
                    self.play_speech()

            sliding_window = ""
            for part in text:
                if not self.speak_worker.work:
                    break
                if isinstance(part, ChatCompletionChunk):
                    part = part.choices[0].delta.content
                    if part is None:
                        part = ""
                sliding_window += part
                if (end_pos := punctuation_rfind(sliding_window)) != -1:
                    sliding_window = sliding_window.removeprefix(
                        (new_part := sliding_window[: end_pos + 1])
                    )
                    handle_part(new_part)
            if isinstance(text, Stream):
                text.close()
            if sliding_window != "":
                handle_part(sliding_window)
            finished = True
            print(colored(result_string, "cyan"))
            state["response"] = result_string
        return
