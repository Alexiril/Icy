""""""

from abc import ABCMeta, abstractmethod

from src import State


class BasicInterface(metaclass=ABCMeta):
    """"""

    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    def before_start(self, state: State) -> None: ...
