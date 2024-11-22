""""""

from pathlib import Path
from typing import Callable, NoReturn
from urllib.request import urlretrieve
from zipfile import ZipFile

from tqdm import tqdm
from vosk import Model

from src.Interfaces import STTInterface


class VoskSTT(STTInterface):
    """"""

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

        return Model(model_path=str(model_path), model_name=model_name)
