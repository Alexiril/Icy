""""""

from json import loads
from pathlib import Path
from typing import Callable, NoReturn
from urllib.request import urlretrieve
from zipfile import ZipFile

from termcolor import colored
from tqdm import tqdm
from vosk import KaldiRecognizer, Model

from src import State
from src.Interfaces import STTInterface


class VoskSTT(STTInterface):
    """"""

    model: Model | None
    model_name: str
    debug: bool
    recognizer: KaldiRecognizer
    _saved_samplerate: int

    @staticmethod
    def vosk_model_loader(model_name: str) -> Model:
        model_path = Path(".") / ".models"
        if not (model_path / model_name).is_dir():

            def hook(
                progress: tqdm[NoReturn],
            ) -> Callable[[int, int, int | None], bool | None]:
                last_blocks: list[int] = [0]

                def update_to(
                    blocks_count: int = 1,
                    block_size: int = 1,
                    total_size: int | None = None,
                ) -> bool | None:
                    if total_size not in (None, -1):
                        progress.total = total_size
                    displayed: bool | None = progress.update(
                        (blocks_count - last_blocks[0]) * block_size
                    )
                    last_blocks[0] = blocks_count
                    return displayed

                return update_to

            with tqdm(
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                miniters=1,
                desc=f"Downloading {model_name}.zip",
            ) as progress:
                urlretrieve(
                    url=f"https://alphacephei.com/vosk/models/{model_name}.zip",
                    filename=str(model_name) + ".zip",
                    reporthook=hook(progress),
                    data=None,
                )
                progress.total = progress.n
                with ZipFile(f"{model_name}.zip", "r") as file:
                    file.extractall(model_path)
                Path(str(model_name) + ".zip").unlink()

        return Model(model_path=str(model_path / model_name))

    def __init__(self) -> None:
        self.model = None
        self.samplerate = 44100
        self._saved_samplerate = 44100
        return

    def recognize(self, data: bytes) -> str:
        if self.model is None:
            raise RuntimeError(
                "Vosk STT recognize was called without before start handler"
            )
        if self.samplerate != self._saved_samplerate:
            self.recognizer = KaldiRecognizer(self.model, self.samplerate)
            self._saved_samplerate = self.samplerate
        if self.recognizer.AcceptWaveform(data):
            return loads(self.recognizer.Result())["text"]
        elif self.debug:
            result: str = loads(self.recognizer.PartialResult())["partial"]
            if result != "":
                print(colored(result, "grey"))
        return ""

    def before_start(self, state: State) -> None:
        if self.model is None or self.model_name != state["settings"]["vosk_model"]:
            self.model_name = state["settings"]["vosk_model"]
            print(colored(f"Vosk model reloading: {self.model_name}", "light_magenta"))
            self.model = VoskSTT.vosk_model_loader(self.model_name)
            print(colored("Vosk model loaded", "light_magenta"))
        self.debug = state["settings"]["vosk_debug"]
        self.recognizer = KaldiRecognizer(self.model, self.samplerate)
        return
