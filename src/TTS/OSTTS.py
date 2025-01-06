""""""

from pathlib import Path
from tempfile import gettempdir
from wave import Wave_read
from wave import open as wave_open

from pyttsx3 import init as pyttsx3_init
from pyttsx3.engine import Engine as TTSEngine
from pyttsx3.voice import Voice

from src import State
from src.Interfaces import TTSInterface


class OSTTS(TTSInterface):
    """"""

    tts_engine: TTSEngine

    def __init__(self) -> None:
        self.tts_engine = pyttsx3_init()
        return

    def before_start(self, state: State) -> None:
        voice = Voice("")
        voice_key = state["settings"]["assistant_voice_key"]
        voice_rate = state["settings"]["assistant_voice_rate"]
        for voice in self.tts_engine.getProperty("voices"):
            if not isinstance(voice, Voice):
                raise Exception("Couldn't load voices for local TTS.")
            if type(voice.name) is not str:
                continue
            if voice_key in voice.name:
                break
        if voice.name is None or voice_key not in voice.name:
            raise Exception(f"Couldn't load a voice '{voice_key}' in local TTS.")
        self.tts_engine.setProperty("voice", voice.id)
        self.tts_engine.setProperty("rate", voice_rate)
        return

    def generate_speech(self, data: str) -> Wave_read:
        data = self.remove_unreadable(data)
        self.tts_engine.save_to_file(
            data,
            (Path(gettempdir()) / "assistant_speech.wav").as_posix(),
        )
        self.tts_engine.runAndWait()
        return wave_open((Path(gettempdir()) / "assistant_speech.wav").as_posix(), "rb")
