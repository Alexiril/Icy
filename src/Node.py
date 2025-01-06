""""""

from abc import ABCMeta, abstractmethod
from sys import stderr, stdout
from time import time
from traceback import print_exc
from types import UnionType
from typing import Literal, NoReturn, Union, get_args, get_origin, overload

from termcolor import colored

from src.State import State
from src.StatePhase import StatePhase


class Node(metaclass=ABCMeta):
    """"""

    __slots__: list[str] = ["left", "right", "name", "requires"]

    left: "Node | None"
    right: "Node | None"

    name: str

    requires: list[tuple[str, type | UnionType]]

    def __init__(
        self,
        name: str,
        left: "Node | None",
        right: "Node | None",
        requires: list[tuple[str, type | UnionType]] = [],
    ) -> None:
        self.name = name
        self.left = left
        self.right = right
        self.requires = requires

    @abstractmethod
    def __call__(self, state: State) -> None: ...

    def __str__(self) -> str:
        return (
            f"[Node '{self.name}'(id:{id(self)})[{type(self).__name__}] passing "
            f"from [{type(self.left).__name__}] to [{type(self.right).__name__}]]"
        )

    def structure_str(self, depth: int = 0, short: bool = False) -> str:
        right = (
            f"{' ' * (depth + 1)}- None"
            if self.right is None
            else self.right.structure_str(depth + 1, short)
        )
        if short:
            return f"{' ' * depth}- {type(self).__name__} ->\n{right}"
        return (
            f"{' ' * depth}- [Node '{self.name}'(id:{id(self)})[{type(self).__name__}]"
            f" ->\n{right}"
        )

    def log_info(self, message: str) -> None:
        current_time = str(round(time(), 3))
        if len(current_time.split(".")[1]) < 3:
            current_time += "0" * (3 - len(current_time.split(".")[1]))
        print(colored(f"[{current_time}] {self}: {message}", "dark_grey"), file=stdout)

    @overload
    def log_error(self, e: Exception, no_return: Literal[False] = ...) -> None: ...

    @overload
    def log_error(self, e: Exception, no_return: Literal[True]) -> NoReturn: ...

    def log_error(self, e: Exception, no_return: bool = False) -> None | NoReturn:
        print_exc(file=stderr)
        current_time = str(round(time(), 3))
        if len(current_time.split(".")[1]) < 3:
            current_time += "0" * (3 - len(current_time.split(".")[1]))
        print(colored(f"[{current_time}] {self}: {e}", "light_red"), file=stderr)
        if no_return:
            raise RuntimeError(str(e))

    def _check_requirements(self, state: State) -> bool:
        dummy = object()
        try:
            for each_req in self.requires:
                if (value := state.get(each_req[0], dummy)) is dummy:
                    return False
                _type = each_req[1]
                if get_origin(_type) is Union:
                    _type = get_args(_type)
                if get_origin(_type) is not None:
                    _type = get_origin(_type)
                if not isinstance(value, _type):  # type: ignore
                    return False
        except Exception as e:
            print(
                colored(
                    f"Exception while checking state requirements: {e}.", "light_red"
                )
            )
        return True

    def run(self, state: State) -> State:
        state.phase = StatePhase.checking
        if not self._check_requirements(state):
            raise RuntimeError(
                f"{self}: requires some arguments ("
                f"{', '.join(map(lambda x: x[0] + ': ' + str(x[1]), self.requires))}) "
                f"the state doesn't have: {state}"
            )
        state.stack.append(self)
        state.phase = StatePhase.processing
        self(state)
        state["from"] = self.name
        if isinstance(self.right, Node):
            state["to"] = self.right.name
            state.phase = StatePhase.passing

            return self.right.run(state)
        state.phase = StatePhase.frozen
        return state
