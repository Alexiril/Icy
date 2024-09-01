from os import listdir
from os.path import isdir
from pathlib import Path
from pdoc import pdoc
from pdoc.render import configure

configure(
    logo="../logo.png",
    logo_link="https://github.com/Alexiril/Icy",
    favicon="../web/favicon.svg",
    footer_text="MIT License. Copyright (c) 2024 Alex Kirel",
)


def find_python_modules(path: Path, exceptions: list[Path]) -> list[Path]:
    result: list[Path] = []
    for fs_obj in listdir(path):
        if fs_obj[0] in "._" or (path / fs_obj) in exceptions:
            continue
        if isdir(path / fs_obj):
            result.extend(find_python_modules(path / fs_obj, exceptions))
        elif "." in fs_obj and fs_obj.split(".")[-1] == "py":
            result.append(path / fs_obj)
    return result


pdoc(
    *find_python_modules(
        Path("."),
        [Path("./modules"), Path("./docs"), Path("./typings"), Path("./utils")],
    ),
    output_directory=Path("docs"),
)
