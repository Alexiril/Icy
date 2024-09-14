"""
Icy is a local hosted assistant, with the main purpose - to make your daily routines
easier. It uses TTS / STT engines with GPT capabilities to help you with any troubles
you would meet on your way using the computer.

This is the main starting file, containing the entry point, command line argument
parsing, and general bot initializing code.
"""

from argparse import ArgumentParser, Namespace
from importlib import import_module
from json import JSONDecodeError, loads
from os import mkdir
from os.path import exists, isdir, isfile
from pathlib import Path
from sys import argv
from threading import Thread
from typing import Any, NoReturn

from termcolor import colored

from appstate import AppState
from assistant import Assistant
from assistant_function import AssistantFunction
from intention_classifier import IntentionClassifier
from module_interface import ModuleInterface
from settings import Settings
from translations import translations
from voice_handler import VoiceHandler
from web import WebServer


def parse_args() -> None:
    """
    Parses the command line arguments and loads the translations for the first time.

    The arguments might be:
    - **--language** (**-l**) [auto] - sets the language code that will be used in the
        web site (and in the bot's commands, if won't be overwritten).

    Aaand yeah, it's all the arguments for now :)

    *Raises*: Doesn't raise itself or handle any exceptions.
    """
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="auto",
        help="language of the configuration web page and terminal",
        required=False,
    )
    args: Namespace = parser.parse_args(argv[1:])
    prev_data_file = Path(".") / "prev.data"

    def set_default_language() -> None:
        if args.language == "auto":
            args.language = "english"

    if exists(prev_data_file) and isfile(prev_data_file):
        try:
            with open(prev_data_file, "rb") as file:
                prev_data: dict[str, Any] = loads(file.read())
                if args.language == "auto":
                    args.language = prev_data.get("language", "english")
        except (OSError, JSONDecodeError):
            set_default_language()
    else:
        set_default_language()

    if not exists(Path(".") / "languages" / f"{args.language}.json"):
        print(
            colored(
                f"Translation to language {args.language} "
                "does't exits. The defaults in use.",
                "red",
            )
        )
    with open(Path(".") / "languages" / f"{args.language}.json") as file:
        translations.update(loads(file.read()))


def init(calculated_config: dict[str, Any]) -> AppState:
    """
    Initializes the bot using the configuration dictionary (it should contain only keys
    presented in the [`Setting`](settings.html) class instances as attirbutes).

    Also, reloads the translations (a chanse for a user to change the languages before
    the bot actually starts) and checks if .models folder exists.

    Returns the [`AppState`](appstate.html) instance ready to run the bot.

    *Raises*: Doesn't raise any exceptions itself. Handles all the instances of
    `Exception` while attempting to initialize the additional modules.
    """
    models_dir = Path(".") / ".models"
    if not exists(models_dir) or not isdir(models_dir):
        mkdir(models_dir)
    state = AppState()
    state.settings = Settings(calculated_config)
    if not exists(Path(".") / "languages" / f"{state.settings.language}.json"):
        print(
            colored(
                f"Translation to language {state.settings.language}"
                " does't exits. The defaults in use.",
                "red",
            )
        )
    with open(Path(".") / "languages" / f"{state.settings.language}.json") as file:
        translations.update(loads(file.read()))
    print(colored(translations["Initialization..."], "light_green"))
    print(colored(translations["Assistant initialization..."], "light_magenta"))
    external_capabilities: dict[str, AssistantFunction] = {}
    for module, module_state in state.settings.modules_states.items():
        if not module_state or not exists(
            Path(".") / "modules" / module / "__init__.py"
        ):
            continue
        try:
            runtime_module = import_module(f"modules.{module}")
            if not hasattr(runtime_module, "Module") or not issubclass(
                runtime_module.Module, ModuleInterface
            ):
                continue
            external_capabilities[module] = runtime_module.Module(state).get_function()
        except Exception as e:
            print(
                colored(
                    f"Couldn't load a module '{module}' due to {type(e)}: {e}", "red"
                )
            )
    state.assistant = Assistant(
        name=state.settings.assistant_name,
        gender=state.settings.assistant_gender,
        voice_key=state.settings.assistant_voice_key,
        gpt_model=state.settings.gpt_model,
        use_chat=state.settings.use_chat,
        gpt_info=state.settings.gpt_info,
        external_capabilities=external_capabilities,
    )
    print(
        colored(translations["Intention classifier initialization..."], "light_magenta")
    )
    state.intention_classifier = IntentionClassifier(state)
    print(colored(translations["STT - TTS system initialization..."], "light_magenta"))
    state.voice_handler = VoiceHandler(
        vosk_model=state.settings.vosk_model,
        vosk_debug=state.settings.vosk_debug,
        voice_key=state.settings.assistant_voice_key,
        voice_rate=state.settings.assistant_voice_rate,
        openai_tts_model=state.settings.openai_tts_model,
        use_openai_tts=state.settings.use_openai_tts,
    )
    print(colored(translations["Initialization completed."], "light_green"))
    return state


def start() -> NoReturn:
    """
    The entry point for Icy assistant. Starts, initializes, runs and shutdowns the
    execution of the bot.

    *Raises*: Nothing itself, also doesn't handle any exception.
    """
    parse_args()
    calculated_config: dict[str, Any] = {}
    server = WebServer(translations=translations, result_config=calculated_config)
    web_server_thread = Thread(target=server.serve_forever)
    web_server_thread.start()

    # Locks the execution of initialization until a user unlocks it via button in the
    # configuration web page (weird solution, I know).
    with server.lock:
        print(colored("Configuration successfully set.", "light_magenta"))

    state: AppState = init(calculated_config=calculated_config)
    setattr(server.RequestHandlerClass, "server_phase", "Runtime")
    state.voice_handler.record(state=state)

    # When recording ends, the program (including the web server) should terminate.
    server.shutdown()
    web_server_thread.join()
    exit(0)
