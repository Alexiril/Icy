from typing import Any
from src import State
from src.Interfaces import ActionInterface


class TestAction2(ActionInterface):
    """"""

    uid: str = "builtin-test-action2"
    keys: list[str] = ["something"]

    def __call__(self, state: State, words: list[str], *args: Any, **kwds: Any) -> None:
        raise NotImplementedError


class QuitAction(ActionInterface):
    """"""

    uid: str = "builtin-quit-action"
    keys: list[str] = ["quit", "force stop"]

    def __call__(self, state: State, words: list[str], *args: Any, **kwds: Any) -> None:
        state["response"] = "Stopping..."
        state["_loops"][-1].execute = False
