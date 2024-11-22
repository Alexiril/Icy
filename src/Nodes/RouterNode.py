""""""

from abc import ABCMeta, abstractmethod

from src import Node, State


class RouterNode(Node, metaclass=ABCMeta):
    """"""

    options: list[Node]

    def __init__(self, left: Node | None, options: list[Node]) -> None:
        super().__init__("Router", left, None)
        self.options = options

    def structure_str(self, depth: int = 0, short: bool = False) -> str:
        right = ""
        for option in self.options:
            right += option.structure_str(depth + 1, short)
        if short:
            return (
                f"{' ' * depth}- {type(self).__name__} -> "
                f"[\n{right}\n{' ' * depth}]"
            )
        return (
            f"{' ' * depth}- [Node '{self.name}'(id:{id(self)})[{type(self).__name__}]"
            f" -> [\n{right}\n{' ' * depth}]"
        )

    @abstractmethod
    def route(self, state: State) -> Node | None: ...

    def __call__(self, state: State) -> None:
        self.right = self.route(state)
