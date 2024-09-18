""""""

from src import Node
from src.Interfaces import AudioInterface, AudioProcessorInterface, STTInterface
from src.State import State


class SpeechGetter(Node):
    """"""

    audio_processors: list[AudioProcessorInterface]

    def __init__(
        self,
        left: Node | None,
        right: Node | None,
        audio_processors: list[AudioProcessorInterface],
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
        data: bytes = state["audio-interface"].input()
        for processor in self.audio_processors:
            data = processor.process(data)
        state["recognized-text"] = state["stt-interface"].recognize(data)
        return
