from http.server import BaseHTTPRequestHandler
from io import BytesIO
from json import JSONDecodeError, dumps, loads
from os import environ, listdir, remove
from os.path import exists, isdir, isfile, join
from pathlib import Path
from queue import Queue
from re import search
from shutil import rmtree
from socket import socket
from socketserver import BaseServer
from threading import Lock
from typing import Any, Literal
from traceback import print_exc as print_traceback
from urllib.parse import unquote
from zipfile import ZipFile

# Don't have stubs for gpt4all
from gpt4all import GPT4All  # type: ignore
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pyttsx3.engine import Engine as TTSEngine
from requests import get, head

from src import State
from src.Functions import load_language

ServerPhase = Literal["Configuration", "Starting", "Runtime"]


class Handler(BaseHTTPRequestHandler):
    state: State
    config_lock: Lock
    server_phase: ServerPhase
    tts_engine: TTSEngine

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
        self.send_header("Server", "Assistant server")
        self.send_header("Date", self.date_time_string())
        self.send_header("Content-Length", str(len(self.output)))
        self.send_header("Location", location)
        self.end_headers()

    def send_headers(self, response_code: int = 200) -> None:
        self.send_response_only(response_code)
        self.send_header("Server", "Assistant server")
        self.send_header("Date", self.date_time_string())
        self.send_header("Content-Length", str(len(self.output)))
        self.end_headers()

    def do_HEAD(self) -> None:
        if self.path == "/":
            env: Environment = Environment(
                loader=FileSystemLoader(
                    (Path(".") / "src" / "Web" / "templates").as_posix()
                ),
                autoescape=select_autoescape(),
            )
            template_file = "blank.html"
            if Handler.server_phase == "Configuration":
                template_file = "config.html"
            elif Handler.server_phase == "Starting":
                template_file = "loader.html"
            elif Handler.server_phase == "Runtime":
                template_file = "index.html"
            template: Template = env.get_template(template_file)
            self.output = template.render(
                translations=Handler.state["translations"][""],
                assistant_name=Handler.state["settings"].get(
                    "assistant_name", "Assistant"
                ),
            ).encode()
            self.send_headers()
        elif (match := search(r"/shared/(.+)", self.path)) is not None:
            with open(
                Path(".") / "src" / "Web" / "shared" / f"{match.group(1)}", "rb"
            ) as file:
                self.output = file.read()
            self.send_headers()
        elif self.path == "/favicon.svg":
            try:
                with open(
                    Path(".") / "src" / "Web" / "shared" / "favicon.svg", "rb"
                ) as file:
                    self.output = file.read()
            except Exception:
                pass
            self.send_headers()
        elif self.path == "/languages":
            models: list[str] = [
                ".".join(file_name.split(".")[:-1])
                for file_name in listdir("languages")
            ]
            self.output = dumps(models).encode()
            self.send_headers()
        elif self.path == "/vosk-models":
            models: list[str] = [
                file_name
                for file_name in listdir(".models")
                if isdir(Path(".") / ".models" / f"{file_name}") and "vosk" in file_name
            ]
            self.output = dumps(models).encode()
            self.send_headers()
        elif self.path == "/voice-keys":
            voices: list[str] = [
                voice.name for voice in Handler.tts_engine.getProperty("voices")
            ]
            self.output = dumps(voices).encode()
            self.send_headers()
        elif self.path == "/gpt-models":
            gpt_models: list[dict[str, Any]] = [
                {"name": x["name"], "filename": x["filename"], "loaded": False}
                for x in GPT4All.list_models()
            ]
            models_ggufs: list[str] = [x["filename"] for x in gpt_models]
            for file in listdir(Path(".") / ".models"):
                if not isfile(Path(".") / ".models" / file):
                    continue
                if file not in models_ggufs:
                    gpt_models.append(
                        {
                            "name": file.removesuffix(".gguf"),
                            "filename": file,
                            "loaded": True,
                        }
                    )
                else:
                    for each in gpt_models:
                        if each["filename"] == file:
                            each["loaded"] = True
            gpt_models.sort(key=lambda x: 0 if x["loaded"] else 1)
            self.output = dumps(gpt_models).encode()
            self.send_headers()
        elif self.path == "/avaliable-modules":

            def get_name_ver(module_path: str) -> list[str]:
                with open(module_path, "rt") as file:
                    app_config: dict[str, Any] = loads(file.read())
                    app_name: str = app_config.get(
                        "name", Handler.state["translations"][""]["Unnamed application"]
                    )
                    app_version = app_config.get("version", "1.0")
                    return [app_name, app_version]

            modules: dict[str, list[str]] = {
                folder_name: get_name_ver(join("modules", folder_name, "module.json"))
                for folder_name in listdir("modules")
                if isdir(join("modules", folder_name))
                and exists(join("modules", folder_name, "module.json"))
            }
            self.output = dumps(modules).encode()
            self.send_headers()
        elif self.path == "/previous-config":
            default_voice_key = "Microsoft Zira Desktop - English (United States)"
            config: dict[str, Any] = {
                "language": Handler.state["translations"][""]["lang_name"],
                "assistant_name": "Assistant",
                "assistant_gender": "Female",
                "assistant_voice_key": default_voice_key,
                "assistant_voice_rate": 150,
                "vosk_model": "vosk-model-en-us-0.42-gigaspeech",
                "vosk_debug": False,
                "use_chat": True,
                "gpt_model": "Phi-3-mini-4k-instruct.Q4_0.gguf",
                "use_openai_gpt": True,
                "use_openai_tts": False,
                "openai_tts_model": "nova",
                "gpt_info": "",
                "modules_states": {},
                "intention_best_proba": 0.5,
            }
            if exists("prev.data"):
                try:
                    with open("prev.data", "rb") as file:
                        prev_data: dict[str, Any] = loads(file.read())
                    config.update(
                        (key, prev_data[key])
                        for key in config.keys() & prev_data.keys()
                    )
                except (OSError, JSONDecodeError):
                    print_traceback()
            openai_token_exists = "OPENAI_API_KEY" in environ
            if openai_token_exists:
                from openai import AuthenticationError, OpenAI

                try:
                    OpenAI().models.list()
                    openai_connection = True
                except AuthenticationError:
                    openai_token_exists = False
                    openai_connection = False
                except Exception:
                    openai_connection = False
            else:
                openai_connection = False
            config["found_openai_token"] = openai_token_exists
            config["have_openai_services_connection"] = openai_connection
            self.output = dumps(config).encode()
            self.send_headers()
        elif self.path == "/translations":
            self.output = dumps(Handler.state["translations"][""]).encode()
            self.send_headers()
        elif self.path == "/run-ai":
            if Handler.server_phase != "Configuration" or not exists("prev.data"):
                self.send_redirect("/")
            Handler.server_phase = "Starting"
            try:
                with open("prev.data") as file:
                    config = loads(file.read())
            except (OSError, JSONDecodeError):
                config = {}
            Handler.state["settings"].update(config)
            Handler.config_lock.release()
            self.send_redirect("/")
        elif self.path == "/phase":
            self.output = self.server_phase.encode()
            self.send_headers()
        elif self.path == "/messages":
            self.output = dumps(
                list(self.state.get("full-dialogue-history", Queue()).queue)
            ).encode()
            self.send_headers()
        elif (match := search(r"/remove-module/(.+)", self.path)) is not None:
            module_id = match.group(1)
            if (module_dir := Path(".") / "modules" / module_id).is_dir():
                try:
                    rmtree(module_dir)
                    self.output = dumps({"result": "ok"}).encode()
                    self.send_headers()
                except Exception as e:
                    self.output = dumps({"result": "error", "reason": e}).encode()
                    self.send_headers(500)
            else:
                self.output = dumps(
                    {"result": "error", "reason": "Module is not installed"}
                ).encode()
                self.send_headers(500)
        elif (
            match := search(r"/install-module/([^&]+)&uri=(.+)", self.path)
        ) is not None:
            module_id = match.group(1)
            load_uri = unquote(match.group(2))
            check = head(load_uri)
            if check.status_code == 200:
                actual_answer = get(load_uri)
                try:
                    zf = ZipFile(BytesIO(actual_answer.content))
                    zf.extractall(Path(".") / "modules" / module_id)
                    self.output = dumps({"result": "ok"}).encode()
                    self.send_headers()
                except Exception as e:
                    self.output = dumps({"result": "error", "reason": e}).encode()
                    self.send_headers(500)
            else:
                actual_answer = get(load_uri)
                if check.status_code != actual_answer.status_code:
                    self.output = dumps(
                        {
                            "result": "error",
                            "reason": (
                                "IPM answer was unstable, "
                                "try installing the module again",
                            ),
                        }
                    ).encode()
                    self.send_headers(500)
                else:
                    self.output = dumps(
                        {"result": "error", "reason": actual_answer.content}
                    ).encode()
                    self.send_headers(500)
        else:
            self.send_headers(404)

    def do_POST_routing(self) -> None:
        try:
            if self.path == "/set-config":
                if (length := self.headers.get("Content-Length")) is None:
                    self.send_headers(400)
                    return
                data: bytes = self.rfile.read(int(length))
                config: dict[str, Any] = loads(data.decode())
                if exists("prev.data"):
                    with open("prev.data", "r") as file:
                        config = loads(file.read())
                    config.update(loads(data.decode()))
                with open("prev.data", "w") as file:
                    file.write(dumps(loads(data.decode())))
                if (
                    lang := config.get(
                        "language", Handler.state["translations"][""]["lang_name"]
                    )
                ) != Handler.state["translations"][""]["lang_name"]:
                    Handler.state["translations"][""].update(load_language(lang, ""))
                self.output = dumps({"result": "ok"}).encode()
                self.send_headers()
            elif self.path == "/reset-ai":
                if exists("prev.data"):
                    remove("prev.data")
                self.output = dumps({"result": "ok"}).encode()
                self.send_headers()
        except Exception as e:
            self.output = dumps({"result": "error", "reason": e}).encode()
            self.send_headers(500)

    def do_GET(self) -> None:
        self.do_HEAD()
        self.wfile.write(self.output)

    def do_POST(self) -> None:
        self.do_POST_routing()
        self.wfile.write(self.output)
