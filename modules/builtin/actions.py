from random import choice
from typing import Any
from src import State
from src.Interfaces import ActionInterface


class HeyAction(ActionInterface):
    """"""

    uid: str = "builtin-hey-action"
    keys: list[str] = ["hey", "listen"]

    def __init__(self, state: State, language: dict[str, Any]) -> None:
        super().__init__(state, language)
        self.keys = self.language["builtin-hey-action-keys"]

    def __call__(self, state: State, words: list[str], *args: Any, **kwds: Any) -> None:
        state["response"] = choice(self.language["builtin-hey-action-response"])


class QuitAction(ActionInterface):
    """"""

    uid: str = "builtin-quit-action"
    keys: list[str] = ["quit", "force stop"]

    def __init__(self, state: State, language: dict[str, Any]) -> None:
        super().__init__(state, language)
        self.keys = self.language["builtin-quit-action-keys"]

    def __call__(self, state: State, words: list[str], *args: Any, **kwds: Any) -> None:
        state["response"] = self.language["builtin-quit-action-response"]
        state["_loops"][-1].execute = False
