""""""

from typing import Iterable

from termcolor import colored

from src import Node
from src.Interfaces import AudioInterface, AudioProcessorInterface, STTInterface
from src.State import State


class SpeechGetter(Node):
    """"""

    audio_processors: Iterable[AudioProcessorInterface]

    def __init__(
        self,
        left: Node | None,
        right: Node | None,
        audio_processors: Iterable[AudioProcessorInterface],
    ) -> None:
        self.audio_processors = audio_processors
        super().__init__(
            "Speech getter node",
            left,
            right,
            [
                ("audio-interface", AudioInterface),
                ("stt-interface", STTInterface),
            ],
        )

    def __call__(self, state: State) -> None:
        state["stt-interface"].samplerate = state["audio-interface"].samplerate
        state["audio-interface"].start_recording()
        print(colored("Listening...", "light_green"))
        while True:
            data: bytes = state["audio-interface"].input()
            for processor in self.audio_processors:
                data = processor.process(data)
            state["recognized-text"] = state["stt-interface"].recognize(data)
            if state["recognized-text"] != "":
                break
        print(colored(state["recognized-text"], "green"))
        state["audio-interface"].stop_recording()
        return
