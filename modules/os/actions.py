from os import P_NOWAIT, spawnv
from os import name as os_name
from shutil import which
from typing import Any
from webbrowser import open as web_open

from termcolor import colored

from src import State
from src.Interfaces import ActionInterface


class OpenApplicationAction(ActionInterface):
    """"""

    uid: str = "os-open-application-action"
    keys: list[str] = ["open", "start"]

    def __init__(self, state: State, language: dict[str, Any]) -> None:
        super().__init__(state, language)
        self.keys = self.language["os-open-application-action-keys"]

    def __call__(self, state: State, words: list[str], *args: Any, **kwds: Any) -> None:
        for word in words:
            if word in self.language["terminal-request"]:
                # windows implementation only now
                if "win" in os_name or "nt" in os_name:
                    self._open_terminal_windows(self.language)
                else:
                    return
                state["response"] = self.language["opening-terminal"]
            elif word in self.language["notepad-request"]:
                # windows implementation only now
                if "win" in os_name or "nt" in os_name:
                    self._open_notepad_windows(self.language)
                else:
                    return
                state["response"] = self.language["opening-notepad"]
            elif word in self.language["calc-request"]:
                # windows implementation only now
                if "win" in os_name or "nt" in os_name:
                    self._open_calc_windows(self.language)
                else:
                    return
                state["response"] = self.language["opening-calc"]
            elif word in self.language["browser-request"]:
                self._open_browser_anyos()
                state["response"] = self.language["opening-browser"]
            else:
                state["response"] = self.language["not-understand-what-to-open"]

    @staticmethod
    def _open_notepad_windows(lang: dict[str, Any]) -> None:
        path = which("notepad")
        if path is None:
            print(colored(lang["error-no-notepad"], "grey"))
            return
        spawnv(P_NOWAIT, path, [path])

    @staticmethod
    def _open_calc_windows(lang: dict[str, Any]) -> None:
        path = which("calc")
        if path is None:
            print(colored(lang["error-no-calc"], "grey"))
            return
        spawnv(P_NOWAIT, path, [path])

    @staticmethod
    def _open_terminal_windows(lang: dict[str, Any]) -> None:
        if (path := which("PowerShell")) is None:
            print(
                colored(
                    lang["error-no-powershell"],
                    "grey",
                )
            )
            path = which("cmd")
            if path is None:
                print(colored(lang["error-no-cmd"], "grey"))
                return
        spawnv(P_NOWAIT, path, [path])

    @staticmethod
    def _open_browser_anyos() -> None:
        web_open("https://www.google.com")
