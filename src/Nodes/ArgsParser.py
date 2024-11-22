""""""

from argparse import ArgumentParser, Namespace
from sys import argv
from typing import Any

from src import Node, State, load_language


class ArgsParser(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "Command line arguments parser",
            left,
            right,
            [("translations", dict[str, dict[str, str]]), ("settings", dict[str, Any])],
        )

    def __call__(self, state: State) -> None:
        parser: ArgumentParser = ArgumentParser()
        parser.add_argument(
            "-l",
            "--language",
            type=str,
            default="auto",
            help="language of the configuration web page and terminal",
            required=False,
        )
        args: Namespace = parser.parse_args(argv[1:])
        if args.language == "auto":
            settings: dict[str, Any] = state["settings"]
            args.language = settings.get("language", "english")
        if args.language == "auto":
            args.language = "english"
        translations = state["translations"]
        if "" not in translations:
            translations[""] = {}
        translations[""].update(
            load_language(language_name=args.language, translation_module="")
        )
        return
