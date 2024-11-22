""""""

from typing import Callable
from re import MULTILINE, compile as re_compile, search
from wave import Wave_read
from src import State
from src.Interfaces import AudioInterface, ResponseViewerInterface, TTSInterface


class PronounceText(ResponseViewerInterface):
    """"""

    state: State | None
    audio: AudioInterface | None
    _text: str
    _text_hook: Callable[[], str]

    def __init__(self) -> None:
        self.state = None
        self.audio = None
        self._text = ""
        return

    def generate_speech(self, text: str) -> Wave_read:
        def remove_unreadable(text: str) -> str:
            text = text.replace("*", "").replace("#", "")
            pattern = re_compile(r"^```(?:.+)\n([\s\S]*?)```$", MULTILINE)
            while (match := search(pattern, text)) is not None:
                text = text[: match.start(0)] + text[match.end(0) :]
            return text

        text = remove_unreadable(text)

        if self.state is None:
            raise RuntimeError(
                "Generate speech was called without before start handler"
            )
        if not isinstance(tts := self.state.get("tts-interface"), TTSInterface):
            raise RuntimeError(
                "TTS interface is not set correctly in the application state"
            )

        return tts.generate_speech(text)

    def view(self, text: str) -> None:
        self._text = text
        speech = self.generate_speech(self._text)

        if self.state is None or self.audio is None:
            raise RuntimeError("Pronounce text was called without before start handler")

        self.audio.output(speech)
        speech.close()

        return

    def hook(self, get_text: Callable[[], str]) -> None:
        self._text_hook = get_text
        self.review()
        return

    def review(self) -> None:
        whole_text = self._text_hook()
        new_text = whole_text.removeprefix(self._text)
        self.view(new_text)
        return

    def before_start(self, state: State) -> None:
        self.state = state
        if not isinstance(audio := self.state.get("audio-interface"), AudioInterface):
            raise RuntimeError(
                "Audio interface is not set correctly in the application state"
            )
        self.audio = audio
        self.audio.set_forse_stop_handler("__force_stop_response")
        return

    def finished(self) -> bool:
        if self.audio is None:
            raise RuntimeError(
                "Finishing check was called without before start handler"
            )
        return self.audio.output_finished()

    def normal_terminate(self) -> None:
        return
