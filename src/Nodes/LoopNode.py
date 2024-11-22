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
        self._first_execute = False
        self.execute = True
        self._initial_values = {}
        self._initial_stack = []
        self._next_after_loop = right

    def __call__(self, state: State) -> None:
        if self._first_execute:
            self.keep_between_iterations.update([*state])
            self._initial_values.update(state)
            self._initial_stack = state.stack.copy()
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
