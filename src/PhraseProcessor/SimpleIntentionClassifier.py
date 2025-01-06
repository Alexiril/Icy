""""""

from re import IGNORECASE, escape, sub
from termcolor import colored

from src import State
from src.Interfaces import PhraseProcessorInterface


class SimpleIntentionClassifier(PhraseProcessorInterface):
    """"""

    state: State | None
    _loaded_modules: list[int]
    _functions: dict[str, str]

    def __init__(self) -> None:
        self._loaded_modules = []
        self._functions = {}
        self.state = None
        return

    def process(self, phrase: str) -> str:
        if self.state is None:
            raise RuntimeError(
                "Intention classifier process was called without before start handler"
            )
        cleared = sub(
            rf'\b{escape(self.state["settings"]["assistant_name"])}\b',
            "",
            phrase,
            flags=IGNORECASE,
        ).strip()
        if cleared == "" or cleared.isspace():
            return phrase
        result: str | None = None
        for key, func in self._functions.items():
            if key in cleared:
                result = func
                break
        if result is None:
            print(colored("Function is not found", "yellow"))
        else:
            print(colored(f"Function is found: {result}", "yellow"))
        return (
            f"{result} {cleared}"
            if result is not None
            else phrase
        )

    def before_start(self, state: State) -> None:
        self.state = state
        if self._loaded_modules != (
            actual_modules := [id(module) for module in state["actions-modules"]]
        ):
            self._loaded_modules = actual_modules
            for action in [
                x
                for module in state["actions-modules"]
                for x in module.get_actions(state)
            ]:
                for option in action.keys:
                    self._functions[option] = action.uid
        return
