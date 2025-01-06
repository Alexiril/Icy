from os import listdir
from pathlib import Path
from typing import Any
from src import State
from src.Functions import stream_to_str
from src.Interfaces import ActionInterface


class SearchInVaultAction(ActionInterface):
    """"""

    uid: str = "obsidian-vault-search-in-vault-action"
    keys: list[str] = ["search in obsidian", "find in obsidian"]

    def __init__(self, state: State, language: dict[str, Any]) -> None:
        super().__init__(state, language)
        self.keys = self.language["obsidian-vault-search-in-vault-action-keys"]

    def __call__(self, state: State, words: list[str], *args: Any, **kwds: Any) -> None:
        s = " ".join(words).replace(self.uid, "")
        for key in sorted(self.keys, key=len):
            s = s.replace(key, "")
        s = s.strip()
        r = self._go_deep(
            state,
            Path(
                state["settings"].get(
                    "obsidian-vault-vaults-path", "./test-obsidian-vaults"
                )
            ),
            s,
        )
        state["response"] = r if r is not None else self.language["not-found-text"]
        return

    def _go_deep(self, state: State, path: Path, s: str) -> str | None:
        for entry in listdir(path):
            if (path / entry).is_dir():
                r = self._go_deep(state, path / entry, s)
                if r is not None:
                    return r
            elif (path / entry).is_file() and entry[-3:] == ".md":
                r = None
                with open(path / entry, "rt", encoding="utf-8") as inp:
                    request = inp.read()
                system_prompt = self.language["search-action-system-prompt"].replace(
                    "%s", s
                )
                answer = stream_to_str(
                    state,
                    state["gpt-interface"].answer(request, state, system_prompt),
                )
                if "none" not in answer.lower():
                    r = answer
                if r is not None:
                    return r
        return None


class MakeANoteAction(ActionInterface):
    """"""

    uid: str = "obsidian-vault-make-a-note-action"
    keys: list[str] = ["make a note in obsidian"]

    def __init__(self, state: State, language: dict[str, Any]) -> None:
        super().__init__(state, language)
        self.keys = self.language["obsidian-vault-make-a-note-action-keys"]

    def __call__(self, state: State, words: list[str], *args: Any, **kwds: Any) -> None:
        s = " ".join(words).replace(self.uid, "")
        for key in sorted(self.keys, key=len):
            s = s.replace(key, "")
        s = s.strip()
        request = s
        system_prompt = self.language["make-note-system-prompt"]
        answer = stream_to_str(
            state,
            state["gpt-interface"].answer(request, state, system_prompt),
        )
        request = self.language["make-note-name-request"] + f"\n{answer}"
        system_prompt = ""
        name = stream_to_str(
            state, state["gpt-interface"].answer(request, state, system_prompt)
        )
        with open(
            Path(
                state["settings"].get(
                    "obsidian-vault-new-notes-vault-path",
                    "./test-obsidian-vaults/test-vault",
                )
            )
            / f"{name}.md",
            "wt",
        ) as output:
            output.write(answer)
        state["response"] = self.language["note-okay"]
        return
