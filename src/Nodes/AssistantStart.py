""""""

from queue import Queue
from src import Node, State


class AssistantStart(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "Assistant start node",
            left,
            right,
            [("translations", dict[str, dict[str, str]])],
        )

    def __call__(self, state: State) -> None:
        state["response"] = state["translations"][""]["I'm ready!"]
        state["assistant-dialogue"] = Queue()
        return
