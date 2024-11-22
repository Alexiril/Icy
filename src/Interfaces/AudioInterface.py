""""""

from abc import ABCMeta, abstractmethod
from wave import Wave_read

from src.Interfaces.BasicInterface import BasicInterface


class AudioInterface(BasicInterface, metaclass=ABCMeta):
    """"""

    samplerate: int

    force_stop_handler: str = ""

    def set_forse_stop_handler(self, state_key: str) -> None:
        self.force_stop_handler = state_key

    @abstractmethod
    def output(self, data: Wave_read) -> None: ...

    @abstractmethod
    def output_finished(self) -> bool: ...

    @abstractmethod
    def start_recording(self) -> None: ...

    @abstractmethod
    def stop_recording(self) -> None: ...

    @abstractmethod
    def input(self) -> bytes: ...

    @abstractmethod
    def clear_input_queue(self) -> None: ...

    @abstractmethod
    def terminate(self) -> None: ...
