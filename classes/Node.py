""""""

from abc import ABCMeta, abstractmethod

from classes.State import State
from classes.StatePhase import StatePhase


class Node(metaclass=ABCMeta):
    """"""

    __slots__: list[str] = ["left", "right", "name", "requires"]

    left: "Node | None"
    right: "Node | None"

    name: str

    requires: list[tuple[str, type]]

    def __init__(
        self,
        name: str,
        left: "Node | None",
        right: "Node | None",
        requires: list[tuple[str, type]] = [],
    ) -> None:
        self.name = name
        self.left = left
        self.right = right

    @abstractmethod
    def __call__(self, state: State): ...

    def __str__(self) -> str:
        return (
            f"[Node '{self.name}'(id:{id(self)})[{type(self).__name__}] passing "
            f"from {self.left} to {self.right}]"
        )

    def _check_requirements(self, state: State) -> bool:
        dummy = object()
        for each_req in self.requires:
            if (value := state.get(each_req[0], dummy)) is dummy:
                return False
            if not isinstance(value, each_req[1]):
                return False
        return True

    def run(self, state: State) -> State:
        state.phase = StatePhase.checking
        if not self._check_requirements(state):
            raise RuntimeError(
                f"The node '{self.name}'(id:{id(self)}) requires some arguments ("
                f"{', '.join(map(lambda x: x[0] + ': ' + str(x[1]), self.requires))}) "
                f"the state doesn't have: {state}"
            )
        state.stack.append(self)
        state.phase = StatePhase.processing
        self(state)
        state["from"] = self.name
        if type(self.right) is Node:
            state["to"] = self.right.name
            state.phase = StatePhase.passing

            return self.right.run(state)
        state.phase = StatePhase.frozen
        return state
