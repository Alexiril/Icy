from http.server import ThreadingHTTPServer
from random import randint
from threading import Lock
from webbrowser import open as web_open

from pyttsx3 import init as pyttsx3_init
from termcolor import colored

from src import State
from src.Web.Handler import Handler


class WebServer(ThreadingHTTPServer):
    def __init__(self, state: State) -> None:
        Handler.state = state
        Handler.server_phase = "Configuration"
        Handler.tts_engine = pyttsx3_init()

        bind_port: int = state["settings"].get("web-bind-port", randint(2000, 40000))
        bind_address: str = state["settings"].get("web-bind-address", "0.0.0.0")
        super().__init__(
            server_address=(bind_address, bind_port), RequestHandlerClass=Handler
        )
        print(
            colored(
                f'{state["translations"][""]["Server started at"]} '
                f'({bind_address}:{bind_port}).',
                "light_magenta",
            )
        )
        page_addr = bind_address if bind_address != "0.0.0.0" else "localhost"
        web_open(f"http://{page_addr}:{bind_port}/")
        self.lock = Lock()
        Handler.config_lock = self.lock
        if not self.lock.acquire():
            raise RuntimeError("Couldn't acquire the configuration lock.")
