""""""

from collections.abc import Callable, Iterable
from importlib import import_module
from inspect import isclass
from json import JSONDecodeError, dumps, loads
from os import listdir
from pathlib import Path
from types import ModuleType
from typing import Any

from openai import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from termcolor import colored

from src.Interfaces import BasicInterface, ModuleInterface
from src.State import State


def get_languages_list() -> set[str]:
    lang_dir: Path = Path(".") / "languages"
    return set([x for x in listdir(lang_dir) if (lang_dir / x).is_file()])


def load_language(language_name: str, translation_module: str) -> dict[str, str]:
    module = Path(".")
    if translation_module != "":
        module /= "modules"
    lang_path: Path = (
        module / translation_module / "languages" / f"{language_name}.json"
    )
    if lang_path.is_file():
        try:
            with open(lang_path, "rb") as file:
                return loads(file.read())
        except (OSError, JSONDecodeError):
            pass
    return {}


def get_modules_list() -> set[str]:
    mod_dir: Path = Path(".") / "modules"
    return set(
        [
            x
            for x in listdir(mod_dir)
            if (mod_dir / x).is_dir() and (mod_dir / x / "module.json").is_file()
        ]
    )


def get_modules_info() -> dict[str, dict[str, Any]]:
    modules_path: Path = Path(".") / "modules"

    def get_data_simple(file: Path) -> bytes:
        with open(file, "rb") as f:
            return f.read()

    result: dict[str, dict[str, Any]] = {
        module: loads(get_data_simple(datafile))
        for module in listdir(modules_path)
        if (datafile := modules_path / module / "module.json").is_file()
    }
    return result


def load_module(name: str, config: dict[str, Any]) -> ModuleInterface | None:
    if not (Path(".") / "modules" / name / "__init__.py").is_file():
        return
    actual_module = import_module(f"modules.{name}")
    module_name = config.get("name", "Unnamed module")
    module_version = config.get("version", "No version")
    if not hasattr(actual_module, "Module") or not issubclass(
        getattr(actual_module, "Module"), ModuleInterface
    ):
        print(
            colored(
                f"Loading module '{module_name}' ({module_version}) "
                "failure: no module found.",
                "light_red",
            )
        )
        return
    translations = {}
    if (langs := Path(".") / "modules" / name / "languages").is_dir():
        for lang in listdir(langs):
            if lang[-5:] == ".json":
                lang_code = lang[:-5]
                try:
                    with open(langs / lang, "rt", encoding="utf-8") as inp:
                        lang_dict = loads(inp.read())
                    translations[lang_code] = lang_dict
                except Exception as e:
                    print(
                        colored(
                            f"Loading module language '{module_name}' "
                            f"({module_version}) : '{lang_code}' "
                            f"failure: {e}.",
                            "light_red",
                        )
                    )
    result = getattr(actual_module, "Module")(config, translations)
    return result


def load_modules(accepted_modules: set[str]) -> list[ModuleInterface]:
    result: list[ModuleInterface] = []
    for name, config in get_modules_info().items():
        if name in accepted_modules:
            module = load_module(name, config)
            if module is not None:
                result.append(module)

    return result


def load_interface[T: BasicInterface](interface: type[T], state: State) -> T:
    intr_name: str = interface.__name__.replace("Interface", "")
    impl_name: str = state["settings"].get(f"{intr_name}_impl", "")
    if impl_name == "":
        raise RuntimeError(
            f"The implementation for '{interface.__name__}' is not set in settings."
        )
    if not (Path(".") / "src" / intr_name / f"{impl_name}.py").exists():
        raise RuntimeError(
            f"The {interface.__name__} name is incorrect: '{impl_name}'."
        )
    module: ModuleType = import_module(f"src.{intr_name}.{impl_name}")
    cls: type[T] = getattr(module, impl_name)
    if not isclass(cls) or not issubclass(cls, interface):
        raise RuntimeError(
            f"The '{impl_name}' doesn't implement the '{interface.__name__}'."
        )
    result = cls()
    result.before_start(state)
    return result


def load_prev() -> dict[str, Any]:
    settings: dict[str, Any] = {}
    prev_data_file: Path = Path(".") / "prev.data"
    if prev_data_file.is_file():
        with open(prev_data_file, "rb") as file:
            settings = loads(file.read())
    return settings


def save_prev(settings: dict[str, Any]) -> None:
    prev_data_file: Path = Path(".") / "prev.data"
    initial_file: bytes = b""
    initial: dict[str, Any] = {}
    try:
        if prev_data_file.is_file():
            with open(prev_data_file, "rb") as original_file:
                initial_file = original_file.read()
                initial = loads(initial_file)
        with open(prev_data_file, "wt") as file:
            initial.update(settings)
            file.write(dumps(initial))
    except (OSError, TypeError) as e:
        print(f"Couldn't save the prev.data file due to {e}.")
        if len(initial_file) == 0:
            return
        print("Attempting to write original prev.data file data back.")
        with open(prev_data_file, "wb") as file:
            file.write(initial_file)
    return


def stream_to_str(
    state: State,
    stream: str | Iterable[str] | Stream[ChatCompletionChunk],
    chunk_callback: Callable[[str, bool, str], None] | None = None,
) -> str:

    if isinstance(stream, str):
        return stream

    punctuation = ".;!?:"
    result_string = ""

    def punctuation_rfind(s: str) -> int:
        index = len(s) - 1
        for symbol in s[::-1]:
            if symbol in punctuation:
                return index
            index -= 1
        return -1

    def handle_part(text: str, final: bool = False) -> None:
        nonlocal result_string
        result_string += text
        if text not in punctuation or final:
            if chunk_callback is not None:
                chunk_callback(text, final, result_string)

    sliding_window = ""
    for part in stream:
        if state.get("__force_stop_stream", False):
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
    if isinstance(stream, Stream):
        stream.close()
    if sliding_window != "":
        handle_part(sliding_window)
    handle_part("", True)
    return result_string
