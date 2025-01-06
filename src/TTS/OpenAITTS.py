""""""

from pathlib import Path
from tempfile import gettempdir
from typing import Literal
from wave import Wave_read
from wave import open as wave_open

from openai import APIStatusError, OpenAI
from termcolor import colored
from src import State
from src.Interfaces import TTSInterface
from src.TTS.OSTTS import OSTTS


class OpenAITTS(TTSInterface):
    """"""

    reserve_interface: TTSInterface = OSTTS()
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self) -> None:
        return

    def before_start(self, state: State) -> None:
        self.reserve_interface.before_start(state)
        self.voice = state["settings"].get("openai_tts_model")
        return

    def generate_speech(self, data: str) -> Wave_read:
        data = self.remove_unreadable(data)

        try:
            OpenAI().audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=data,
                response_format="wav",
            ).write_to_file((Path(gettempdir()) / "assistant_speech.wav").as_posix())
            return wave_open(
                (Path(gettempdir()) / "assistant_speech.wav").as_posix(), "rb"
            )
        except APIStatusError as e:
            print(colored(f"OpenAI services are unavaliable: {e}.", "light_red"))
        except Exception as e:
            print(
                colored(
                    f"Exception while running OpenAI TTS request: {e}.", "light_red"
                )
            )
        return self.reserve_interface.generate_speech(data)
