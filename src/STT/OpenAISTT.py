""""""

from src import State
from src.Interfaces import STTInterface


class OpenAISTT(STTInterface):
    """"""

    def __init__(self) -> None:
        raise NotImplementedError

    def before_start(self, state: State) -> None:
        raise NotImplementedError

    def recognize(self, data: bytes) -> str:
        raise NotImplementedError
