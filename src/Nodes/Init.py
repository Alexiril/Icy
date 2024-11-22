"""This module contains nodes entrypoint"""

from src import Node
from src.State import State


class Init(Node):
    """"""

    def __init__(self, right: Node | None) -> None:
        super().__init__("Icy init node", None, right)

    def __call__(self, state: State) -> None:
        state["translations"] = {}
        state["settings"] = {}
        return
