""""""

from json import JSONDecodeError, loads
from os import listdir
from pathlib import Path
from typing import Any


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
