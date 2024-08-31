from http.server import ThreadingHTTPServer
from random import randint
from threading import Lock
from typing import Any
from webbrowser import open as web_open

from pyttsx3 import init as pyttsx3_init
from termcolor import colored

from translations import Translations
from web.handler import Handler


class WebServer(ThreadingHTTPServer):

    def __init__(
        self, translations: Translations, result_config: dict[str, Any]
    ) -> None:
        Handler.translations = translations
        Handler.result_config = result_config
        Handler.server_phase = "Configuration"
        Handler.tts_engine = pyttsx3_init()
        bind_port: int = randint(2000, 40000)
        bind_address: str = "0.0.0.0"
        super().__init__(
            server_address=(bind_address, bind_port), RequestHandlerClass=Handler
        )
        print(
            colored(
                f'{translations["Server started at"]} ({bind_address}:{bind_port}).',
                "light_magenta",
            )
        )
        web_open(f"http://localhost:{bind_port}/")
        self.lock = Lock()
        Handler.config_lock = self.lock
        if not self.lock.acquire():
            raise RuntimeError("Couldn't acquire the configuration lock.")
