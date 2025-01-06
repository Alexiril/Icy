from http.server import ThreadingHTTPServer

from termcolor import colored

from ipm.Handler import Handler


class WebServer(ThreadingHTTPServer):
    def __init__(self) -> None:
        bind_port: int = 80
        bind_address: str = "0.0.0.0"
        super().__init__(
            server_address=(bind_address, bind_port), RequestHandlerClass=Handler
        )
        print(
            colored(
                'Packet manager server initialized at '
                f'({bind_address}:{bind_port}).',
                "light_magenta",
            )
        )
