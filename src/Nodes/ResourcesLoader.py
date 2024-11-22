""""""

from typing import Any

from src import (
    Node,
    State,
    load_interface,
    load_modules,
)
from src.Interfaces import AudioInterface, GPTInterface, STTInterface, TTSInterface


class ResourcesLoader(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "External resources and modules loader",
            left,
            right,
            [("settings", dict[str, Any])],
        )

    def __call__(self, state: State) -> None:
        try:
            state["stt-interface"] = load_interface(STTInterface, state)
            state["tts-interface"] = load_interface(TTSInterface, state)
            state["gpt-interface"] = load_interface(GPTInterface, state)
            state["audio-interface"] = load_interface(AudioInterface, state)
            state["external-modules"] = load_modules(
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
        except Exception as e:
            self.log_error(e, True)
        return
