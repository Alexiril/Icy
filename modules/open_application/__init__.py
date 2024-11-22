# TODO
# add linux and macos implementation

from json import loads
from os import P_NOWAIT
from os import name as os_name
from os import spawnv
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING
from webbrowser import open as web_open

from termcolor import colored

from src.AssistantAction import AssistantAction
from src.ModuleInterface import ModuleInterface

if TYPE_CHECKING:
    from appstate import AppState


class Module(ModuleInterface):
    def __init__(self, state: "AppState") -> None:
        super().__init__(state)

        with open(
            Path(".") / "modules" / "open_application" / "module.json", "rt"
        ) as file:
            self.module_config = loads(file.read())

        self.terminal_options: list[str] = [
            self.module_config["translations"][self.state.settings.language][
                "terminal"
            ],
            self.module_config["translations"][self.state.settings.language]["console"],
            self.module_config["translations"][self.state.settings.language]["shell"],
        ]

        self.browser_options: list[str] = [
            self.module_config["translations"][self.state.settings.language]["browser"],
            self.module_config["translations"][self.state.settings.language][
                "internet"
            ],
        ]

    def _open_terminal_windows(self) -> None:
        if (path := which("PowerShell")) is None:
            print(
                colored(
                    self.module_config["translations"][self.state.settings.language][
                        "Couldn't find PowerShell, rolling back to Command line"
                    ],
                    "grey",
                )
            )
            path = "cmd"
        spawnv(P_NOWAIT, path, [])

    def _open_browser_anyos(self) -> None:
        web_open("")

    def _open_application(self, state: "AppState", *args: str) -> None:
        for arg in args:
            if arg in self.terminal_options:
                # windows implementation only now
                if "win" in os_name or "nt" in os_name:
                    self._open_terminal_windows()
                else:
                    return
            if arg in self.browser_options:
                self._open_browser_anyos()

    def get_function(self) -> AssistantAction:
        return AssistantAction(
            [
                self.module_config["translations"][self.state.settings.language][
                    "open"
                ],
                self.module_config["translations"][self.state.settings.language][
                    "start"
                ],
            ],
            self._open_application,
        )
