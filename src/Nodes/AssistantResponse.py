""""""

from queue import Queue
from time import sleep
from typing import Any, Iterable

from openai import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from termcolor import colored

from src import Node, State, stream_to_str
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
                ("full-dialogue-history", Queue[dict[str, str]]),
                ("settings", dict[str, Any]),
                ("response", str | Iterable[str] | Stream[ChatCompletionChunk]),  # type: ignore # noqa: E501
            ],
        )

    def __call__(self, state: State) -> None:
        response: str | Iterable[str] | Stream[ChatCompletionChunk] = state["response"]
        if response == "":
            return

        state["__force_stop_stream"] = False

        if isinstance(response, str):
            print(colored(response, "cyan"))
            state["full-dialogue-history"].put(
                {"role": "assistant", "content": response}
            )
            for viewer in self.viewers:
                viewer.before_start(state)
                viewer.view(response)
            while not state["__force_stop_stream"] and not all(
                [x.finished() for x in self.viewers]
            ):
                sleep(0.5)
            for viewer in self.viewers:
                viewer.normal_terminate()
            return

        result_string = ""

        for viewer in self.viewers:
            viewer.before_start(state)
            viewer.hook(lambda: result_string)

        def chunk_callback(new_chunk: str, final: bool, entire_string: str) -> None:
            nonlocal result_string
            result_string = entire_string
            if not final:
                for viewer in self.viewers:
                    viewer.review()
                while not state["__force_stop_stream"] and not all(
                    [x.finished() for x in self.viewers]
                ):
                    sleep(0.5)
            else:
                for viewer in self.viewers:
                    viewer.normal_terminate()

        result_string = stream_to_str(state, response, chunk_callback)

        print(colored(result_string, "cyan"))
        state["full-dialogue-history"].put(
            {"role": "assistant", "content": result_string}
        )
        state["response"] = result_string
        return
