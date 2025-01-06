from hashlib import sha256
from http.server import BaseHTTPRequestHandler
from json import dumps
from pathlib import Path
from re import search
from socket import socket
from socketserver import BaseServer
from typing import Any


class Handler(BaseHTTPRequestHandler):
    def __init__(
        self,
        request: socket | tuple[bytes, socket],
        client_address: Any,
        server: BaseServer,
    ) -> None:
        self.output: bytes = b""
        super().__init__(request=request, client_address=client_address, server=server)

    def send_redirect(self, location: str) -> None:
        self.send_response_only(302)
        self.send_header("Server", "Icy packet manager server")
        self.send_header("Date", self.date_time_string())
        self.send_header("Content-Length", str(len(self.output)))
        self.send_header("Location", location)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def send_headers(self, response_code: int = 200) -> None:
        self.send_response_only(response_code)
        self.send_header("Server", "Icy packet manager server")
        self.send_header("Date", self.date_time_string())
        self.send_header("Content-Length", str(len(self.output)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_HEAD(self) -> None:
        if self.path == "/api/get-packed-list":
            with open(Path(".") / "ipm" / "packed" / "packed.json", "rb") as inp:
                self.output = inp.read()
            self.send_headers()
        elif (
            match := search(r"/api/packed/([^&]+)&ver=([^&]+)&hash=(.+)", self.path)
        ) is not None:
            name = match.group(1)
            version = match.group(2)
            hash = match.group(3)
            filename = f"{name}.{version}.zip"
            if (f := (Path(".") / "ipm" / "packed" / filename)).exists():
                with open(f, "rb") as inp:
                    result = inp.read()
                if (actual_hash := sha256(result).hexdigest()) == hash:
                    self.output = result
                    self.send_headers()
                else:
                    self.output = dumps(
                        {"error": f"File {filename} has hash {actual_hash}"}
                    ).encode()
                    self.send_headers(404)
            else:
                self.output = dumps(
                    {"error": f"File {filename} is not found"}
                ).encode()
                self.send_headers(404)
        else:
            self.send_headers(404)

    def do_POST_routing(self) -> None:
        try:
            if self.path == "/" and False:  # just for remembering the structure
                pass
            else:
                self.send_headers(404)
        except Exception as e:
            self.output = dumps({"result": "error", "reason": e}).encode()
            self.send_headers(500)

    def do_GET(self) -> None:
        self.do_HEAD()
        self.wfile.write(self.output)

    def do_POST(self) -> None:
        self.do_POST_routing()
        self.wfile.write(self.output)
