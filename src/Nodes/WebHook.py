""""""

from src import Node, State
from src.Web import WebServer


class WebHook(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "Assistant web server phase hook",
            left,
            right,
            [("web-server", WebServer)]
        )

    def __call__(self, state: State) -> None:
        state["web-server"].RequestHandlerClass.server_phase = "Runtime"
        return
