""""""

from queue import Queue

from openai.types.chat import ChatCompletionMessageParam

from src import Node, State
from src.Interfaces import GPTInterface, ModuleInterface, PhraseProcessorInterface


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
                ("actions-modules", list[ModuleInterface]),
            ],
        )

    def __call__(self, state: State) -> None:
        if "chat-mode" not in state:
            state["chat-mode"] = False
        text: str = state["recognized-text"]
        for processor in self.phrase_processors:
            text = processor.process(text)
        request: str = text.lower()
        words: list[str] = request.split(" ")
        for action in state["actions-modules"].get_actions():
            if action.uid == words[0]:
                action(state, words)
                return
        state["gpt-interface"].answer(request, state)
        return
