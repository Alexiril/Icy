""""""

from queue import Queue
from typing import Any, Iterable

from openai.types.chat import ChatCompletionMessageParam

from src import Node, State
from src.Interfaces import GPTInterface, ModuleInterface, PhraseProcessorInterface


class AssistantRunner(Node):
    """"""

    phrase_processors: Iterable[PhraseProcessorInterface]

    def __init__(
        self,
        left: Node | None,
        right: Node | None,
        phrase_processors: Iterable[PhraseProcessorInterface],
    ) -> None:
        self.phrase_processors = phrase_processors
        self.chat_mode = False
        super().__init__(
            "Assistant runner node",
            left,
            right,
            [
                ("full-dialogue-history", Queue[dict[str, str]]),
                ("assistant-dialogue", Queue[ChatCompletionMessageParam]),
                ("recognized-text", str),
                ("gpt-interface", GPTInterface),
                ("actions-modules", list[ModuleInterface]),
                ("settings", dict[str, Any]),
            ],
        )

    def __call__(self, state: State) -> None:
        state["response"] = ""
        if "chat-mode" not in state:
            state["chat-mode"] = False
        text: str = state["recognized-text"]
        if state["settings"]["assistant_name"].lower() not in text:
            return
        state["full-dialogue-history"].put({"role": "user", "content": text})
        for processor in self.phrase_processors:
            processor.before_start(state)
            text = processor.process(text)
        request: str = text.lower()
        words: list[str] = request.split(" ")
        for action in [
            x for module in state["actions-modules"] for x in module.get_actions(state)
        ]:
            if action.uid == words[0]:
                action(state, words)
                return
        if state["settings"]["use_chat"]:
            state["assistant-dialogue"].put(
                {
                    "role": "user",
                    "content": request,
                }
            )
            state["response"] = state["gpt-interface"].answer(request, state)
            state["gpt-answered"] = True
        return
