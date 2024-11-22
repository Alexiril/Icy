""""""

from typing import Any

from src import Node, State


class LoopNode(Node):
    """"""

    keep_between_iterations: set[str]
    execute: bool

    _first_execute: bool
    _initial_values: dict[str, Any]
    _initial_stack: list[Node]
    _next_after_loop: Node | None

    def __init__(
        self,
        left: Node | None,
        inside: Node,
        right: Node | None,
        keep_between_iterations: set[str] = set(),
    ) -> None:
        super().__init__("Loop", left, inside)
        self.keep_between_iterations = keep_between_iterations
        self._first_execute = True
        self.execute = True
        self._initial_values = {}
        self._initial_stack = []
        self._next_after_loop = right

    def structure_str(self, depth: int = 0, short: bool = False) -> str:
        if hasattr(self, "__structure_str_passed"):
            delattr(self, "__structure_str_passed")
            return f"{' ' * depth}- {type(self).__name__} [...]"
        setattr(self, "__structure_str_passed", True)
        right = (
            f"{' ' * (depth + 1)}- None"
            if self._next_after_loop is None
            else self._next_after_loop.structure_str(depth + 1, short)
        )
        inside = (
            f"{' ' * (depth + 1)}- None"
            if self.right is None
            else self.right.structure_str(depth + 1, short)
        )
        while inside[-1] in ('\n', ' '):
            inside = inside[:-1]
        if short:
            return (
                f"{' ' * depth}- {type(self).__name__} : "
                f"[\n{inside}\n{' ' * depth}] ->\n{right}"
            )
        return (
            f"{' ' * depth}- [Node '{self.name}'(id:{id(self)})[{type(self).__name__}]"
            f" : [\n{inside}\n{' ' * depth}] ->\n{right}"
        )

    def __call__(self, state: State) -> None:
        if self._first_execute:
            self.keep_between_iterations.update([*state])
            self._initial_values.update(state)
            self._initial_stack = state.stack.copy()
            self._first_execute = False
        args: list[str] = [
            key for key in state if key not in self.keep_between_iterations
        ]
        for arg in args:
            if arg in self._initial_values:
                state[arg] = self._initial_values[arg]
            else:
                state.pop(arg)
        state.stack = self._initial_stack.copy()
        if not self.execute:
            self.right = self._next_after_loop
            return
        if (loops := state.get("_loops", None)) is None:
            state["_loops"] = []
            loops: list[LoopNode] = state["_loops"]
        loops.append(self)
        return
