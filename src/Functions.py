""""""

from importlib import import_module
from inspect import isclass
from json import JSONDecodeError, loads
from os import listdir
from pathlib import Path
from traceback import print_exc
from types import ModuleType
from typing import Any

from termcolor import colored

from src.ExternalModule import ExternalModule
from src.Interfaces import BasicInterface
from src.State import State
from src.Node import Node


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


def load_module(name: str, config: dict[str, Any]) -> ExternalModule | None:
    if not (Path(".") / "modules" / name / "__init__.py").is_file():
        return
    try:
        runtime_module = import_module(f"modules.{name}")
        if not hasattr(runtime_module, "Module") or not issubclass(
            runtime_module.Module, Node
        ):
            return
        return ExternalModule(
            config,
            runtime_module,
        )
    except Exception as e:
        print_exc()
        print(colored(f"Loading module failure: {e}", "light_red"))
        return


def load_modules(accepted_modules: set[str]) -> list[ExternalModule]:
    result: list[ExternalModule] = []
    for name, config in get_modules_info().items():
        if name in accepted_modules:
            module = load_module(name, config)
            if module is not None:
                result.append(module)

    return result


def load_interface[T: BasicInterface](interface: type[T], state: State) -> T:
    intr_name: str = interface.__name__.replace("Interface", "")
    impl_name: str = state["settings"].get(f"{intr_name}-impl", "")
    if (
        impl_name == ""
        or not (Path(".") / "src" / intr_name / f"{impl_name}.py").exists()
    ):
        raise RuntimeError(
            f"The {interface.__name__} name is incorrect: '{impl_name}'."
        )
    module: ModuleType = import_module(f"src.{intr_name}.{impl_name}")
    cls: type[T] = getattr(module, impl_name)
    if not isclass(cls) or not issubclass(cls, interface):
        raise RuntimeError(
            f"The '{impl_name}' doesn't implement the '{interface.__name__}'."
        )
    return cls(state)
