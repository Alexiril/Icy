"""This module contains nodes exitpoint"""

from src import Node
from src.State import State


class Quit(Node):
    """"""

    def __init__(self, left: Node | None) -> None:
        super().__init__("Icy quit node", left, None)

    def __call__(self, state: State) -> None:
        if (server := state.get("web-server")) is not None:
            server.shutdown()
            state["web-server-thread"].join()
        if (audio := state.get("audio-interface")) is not None:
            audio.terminate()
        return
