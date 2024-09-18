""""""

from queue import Queue

from openai.types.chat import ChatCompletionMessageParam

from src import ExternalModule, Node
from src.Interfaces import GPTInterface, PhraseProcessorInterface
from src.State import State


class AssistantRunner(Node):
    """"""

    phrase_processors: list[PhraseProcessorInterface]

    def __init__(
        self,
        left: Node | None,
        right: Node | None,
        phrase_processors: list[PhraseProcessorInterface],
    ) -> None:
        self.phrase_processors = phrase_processors
        self.chat_mode = False
        super().__init__(
            "Assistant runner node",
            left,
            right,
            [
                ("assistant-dialogue", Queue[ChatCompletionMessageParam]),
                ("recognized-text", str),
                ("gpt-interface", GPTInterface),
                ("external-modules", list[ExternalModule]),
            ],
        )

    def __call__(self, state: State) -> None:
        if "chat-mode" not in state:
            state["chat-mode"] = False
        text = state["recognized-text"]
        for processor in self.phrase_processors:
            text = processor.process(text)
        words: list[str] = text.lower().split(" ")
        return
