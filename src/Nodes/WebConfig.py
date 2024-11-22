""""""

from threading import Thread
from typing import Any

from src import Node, State
from src.Web import WebServer


class WebConfig(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__(
            "Web server configuration controller",
            left,
            right,
            [("translations", dict[str, dict[str, str]]), ("settings", dict[str, Any])],
        )

    def __call__(self, state: State) -> None:
        server = WebServer(state)

        web_server_thread = Thread(target=server.serve_forever)
        web_server_thread.start()

        # Locks the execution of initialization until a user unlocks it via button in
        # the configuration web page (weird solution, I know).
        with server.lock:
            state["web-server"] = server
            state["web-server-thread"] = web_server_thread

            return
