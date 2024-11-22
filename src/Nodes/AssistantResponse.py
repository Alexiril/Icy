""""""

from time import sleep
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
                ("response", str | Iterable[str] | Stream[ChatCompletionChunk]),
            ],
        )

    def __call__(self, state: State) -> None:
        response: str | Iterable[str] | Stream[ChatCompletionChunk] = state["response"]
        if response == "":
            return

        state["__force_stop_response"] = False

        if isinstance(response, str):
            print(colored(response, "cyan"))
            for viewer in self.viewers:
                viewer.before_start(state)
                viewer.view(response)
            while not state["__force_stop_response"] and not all(
                [x.finished() for x in self.viewers]
            ):
                sleep(0.5)
            for viewer in self.viewers:
                viewer.normal_terminate()
            return

        state["stop-chunk-loading"] = False
        punctuation = ".;!?:"
        result_string = ""

        for viewer in self.viewers:
            viewer.before_start(state)
            viewer.hook(lambda: result_string)

        def punctuation_rfind(s: str) -> int:
            index = len(s) - 1
            for symbol in s[::-1]:
                if symbol in punctuation:
                    return index
                index -= 1
            return -1

        def handle_part(text: str, final: bool = False) -> None:
            nonlocal result_string
            result_string += text
            if text not in punctuation or final:
                for viewer in self.viewers:
                    viewer.review()
                while not state["__force_stop_response"] and not all(
                    [x.finished() for x in self.viewers]
                ):
                    sleep(0.5)

        sliding_window = ""
        for part in response:
            if state["stop-chunk-loading"]:
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
        if isinstance(response, Stream):
            response.close()
        if sliding_window != "":
            handle_part(sliding_window)
        handle_part("", True)
        for viewer in self.viewers:
            viewer.normal_terminate()
        print(colored(result_string, "cyan"))
        state["response"] = result_string
        return
