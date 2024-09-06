from json import loads
from os.path import exists
from queue import Queue
from re import MULTILINE, search
from re import compile as re_compile
from tempfile import gettempdir
from threading import Lock
from traceback import print_exc as print_traceback
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Iterable
from wave import open as wave_open

from openai import APIStatusError, OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from pyaudio import PyAudio
from pyttsx3.engine import Engine as TTSEngine
from pyttsx3 import init as pyttsx3_init
from pyttsx3.voice import Voice
from termcolor import colored
from vosk import KaldiRecognizer, Model

# Too hard to make typings stubs.
from sounddevice import RawInputStream, query_devices  # type: ignore

from message_window import MessageWindow
from settings import OpenAITTSVoice
from translations import translations

if TYPE_CHECKING:
    from appstate import AppState


class VoiceHandler:
    tts_engine: TTSEngine
    model: Model
    recording_queue: Queue[bytes]
    recording_lock: Lock
    vosk_debug: bool
    openai_tts_model: OpenAITTSVoice
    use_openai_tts: bool
    speak_worker: SimpleNamespace

    class StopRecording(Exception):
        ...

    def __init__(
        self,
        vosk_model: str,
        vosk_debug: bool,
        voice_key: str,
        voice_rate: int,
        openai_tts_model: OpenAITTSVoice,
        use_openai_tts: bool,
    ) -> None:
        self.speak_worker = SimpleNamespace(work=True)
        self.vosk_debug = vosk_debug
        self.openai_tts_model = openai_tts_model
        self.use_openai_tts = use_openai_tts
        self.tts_engine = pyttsx3_init()
        voice = Voice("")
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
        if not exists(f".models/{vosk_model}"):
            print(
                colored(
                    f'{translations["Please download the model from:"]}\n'
                    'https://alphacephei.com/vosk/models '
                    f'{translations["and unpack the archive into .models folder."]}',
                    "red",
                )
            )
            raise FileNotFoundError("Vosk recognizer model")
        self.model = Model(f".models/{vosk_model}")
        self.recording_queue = Queue()
        self.recording_lock = Lock()

    def generate_speech(self, text: str) -> None:
        def remove_unreadable(text: str) -> str:
            text = text.replace("*", "").replace("#", "")
            pattern = re_compile(r"^```(?:.+)\n([\s\S]*?)```$", MULTILINE)
            while (match := search(pattern, text)) is not None:
                text = text[: match.start(0)] + text[match.end(0):]
            return text

        def offline_tts():
            self.tts_engine.save_to_file(
                remove_unreadable(text),
                f"{gettempdir()}/assistant_speech.wav",
            )
            self.tts_engine.runAndWait()

        if not self.use_openai_tts:
            return offline_tts()
        try:
            OpenAI().audio.speech.create(
                model="tts-1",
                voice=self.openai_tts_model,
                input=remove_unreadable(text),
                response_format="wav",
            ).write_to_file(f"{gettempdir()}/assistant_speech.wav")
            return
        except APIStatusError:
            print(colored("OpenAI services are unavaliable.", "light_red"))
        except Exception:
            print_traceback()
        return offline_tts()

    def play_speech(self) -> None:
        self.speak_worker.work = True
        with self.recording_lock:
            chunk: int = 8000
            audio = PyAudio()
            with wave_open(f"{gettempdir()}/assistant_speech.wav", "rb") as file:
                stream = audio.open(
                    format=audio.get_format_from_width(file.getsampwidth()),
                    channels=file.getnchannels(),
                    rate=file.getframerate(),
                    output=True,
                )
                while (data := file.readframes(chunk)) and self.speak_worker.work:
                    stream.write(data)
                stream.stop_stream()
                stream.close()
            audio.terminate()

    def say(self, text: str | Iterable[str] | Stream[ChatCompletionChunk]) -> str:
        if type(text) is str:
            result_string = text
            print(colored(text, "cyan"))
            self.generate_speech(text)
            MessageWindow(
                text=text,
                show=self.recording_lock.locked,
                speak_worker=self.speak_worker,
            )
            self.play_speech()
        else:
            punctuation = ".;!?:"
            result_string = ""

            def update_text() -> str:
                return result_string

            finished: bool = False
            MessageWindow(
                text=update_text,
                show=lambda: not finished,
                speak_worker=self.speak_worker,
            )

            def punctuation_rfind(s: str) -> int:
                index = len(s) - 1
                for symbol in s[::-1]:
                    if symbol in punctuation:
                        return index
                    index -= 1
                return -1

            def handle_part(text: str) -> None:
                nonlocal result_string
                result_string += text
                if text not in punctuation:
                    self.generate_speech(text)
                    self.play_speech()

            sliding_window = ""
            for part in text:
                if not self.speak_worker.work:
                    break
                if isinstance(part, ChatCompletionChunk):
                    part = part.choices[0].delta.content
                    if part is None:
                        part = ""
                sliding_window += part
                if (end_pos := punctuation_rfind(sliding_window)) != -1:
                    sliding_window = sliding_window.removeprefix(
                        (new_part := sliding_window[: end_pos + 1])
                    )
                    handle_part(new_part)
            if isinstance(text, Stream):
                text.close()
            if sliding_window != "":
                handle_part(sliding_window)
            finished = True
            print(colored(result_string, "cyan"))

        return result_string

    def _chunk_callback(self, indata: Any, frames: Any, time: Any, status: Any) -> None:
        if status:
            print(
                colored(
                    f'{translations["Sound device status updated:"]} {status}', "red"
                )
            )
        if self.recording_lock.locked():
            return
        with self.recording_lock:
            self.recording_queue.put(bytes(indata))

    def record(self, state: "AppState") -> None:
        while True:
            try:
                device_info: dict[str, Any] = query_devices(  # type: ignore
                    device=None, kind="input"
                )
                samplerate = device_info["default_samplerate"]
                with RawInputStream(
                    samplerate=samplerate,
                    blocksize=8000,
                    dtype="int16",
                    channels=1,
                    callback=self._chunk_callback,
                ):
                    print(colored(translations["Ready, listening..."], "light_yellow"))
                    self.say(translations["I'm ready!"])
                    recognizer = KaldiRecognizer(self.model, samplerate)
                    while True:
                        data: bytes = self.recording_queue.get()
                        if recognizer.AcceptWaveform(data):
                            state.assistant.handle_request(
                                state=state, request=loads(recognizer.Result())["text"]
                            )
                        elif self.vosk_debug:
                            result: str = loads(recognizer.PartialResult())["partial"]
                            if result != "":
                                print(colored(result, "grey"))
            except VoiceHandler.StopRecording:
                return
            except KeyboardInterrupt:
                return
            except Exception:
                print_traceback()
