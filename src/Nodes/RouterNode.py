""""""

from abc import ABCMeta, abstractmethod

from src import Node, State


class RouterNode(Node, metaclass=ABCMeta):
    """"""

    options: list[Node]

    def __init__(self, left: Node | None, options: list[Node]) -> None:
        super().__init__("Router", left, None)
        self.options = options

    @abstractmethod
    def route(self, state: State) -> Node | None:
        ...

    def __call__(self, state: State) -> None:
        self.right = self.route(state)
