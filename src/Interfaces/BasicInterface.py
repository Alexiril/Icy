""""""

from abc import ABCMeta, abstractmethod

from src.State import State


class BasicInterface(metaclass=ABCMeta):
    """"""

    @abstractmethod
    def __init__(self, state: State) -> None: ...
