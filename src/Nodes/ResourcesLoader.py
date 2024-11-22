""""""

from importlib import import_module
from pathlib import Path
from typing import Any, Callable, NoReturn
from urllib.request import urlretrieve
from zipfile import ZipFile

# Don't have stubs for gpt4all, no time to make them.
from gpt4all import GPT4All  # type: ignore
from termcolor import colored
from tqdm import tqdm
from vosk import Model

from src import ExternalModule, Node, State, get_modules_info


class ResourcesLoader(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "External resources and modules loader",
            left,
            right,
            [("settings", dict[str, Any])],
        )

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

    @staticmethod
    def gpt4all_model_loader(model_name: str) -> GPT4All:
        # Auto downloading is something...
        return GPT4All(model_name=model_name, model_path=Path(".") / ".models")

    @staticmethod
    def modules_loader(accepted_modules: set[str]) -> list[ExternalModule]:
        result: list[ExternalModule] = []
        for name, config in get_modules_info().items():
            if (
                name not in accepted_modules
                or not (Path(".") / "modules" / name / "__init__.py").is_file()
            ):
                continue
            try:
                runtime_module = import_module(f"modules.{name}")
                if not hasattr(runtime_module, "Module") or not issubclass(
                    runtime_module.Module, Node
                ):
                    continue
                result.append(
                    ExternalModule(
                        config,
                        runtime_module,
                    )
                )
            except Exception as e:
                print(
                    colored(
                        f"Couldn't load a module '{name}' due to {type(e)}: {e}",
                        "red",
                    )
                )

        return result

    def __call__(self, state: State) -> None:
        state["vosk-model"] = ResourcesLoader.vosk_model_loader(
            state["settings"].get("vosk_model", "")
        )
        state["gpt-model"] = ResourcesLoader.gpt4all_model_loader(
            state["settings"].get("gpt_model", "")
        )
        state["external-modules"] = ResourcesLoader.modules_loader(
            set(
                [
                    name
                    for name, acc in state["settings"]
                    .get("modules_states", dict())
                    .items()
                    if acc
                ]
            )
        )
        return
