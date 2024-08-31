# TODO
# add correct index web page for assistant
# handle the obsidian vault
# save web page theme
# add headless (no web / no window) mode

from argparse import ArgumentParser, Namespace
from importlib import import_module
from json import loads
from os.path import exists, join
from sys import argv
from threading import Thread
from typing import Any

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

_calculated_config: dict[str, Any] = {}


def init() -> AppState:
    global _calculated_config
    state = AppState()
    state.settings = Settings(_calculated_config)
    if not exists(f"languages/{state.settings.language}.json"):
        print(
            colored(
                f"Translation to language {state.settings.language}"
                " does't exits. The defaults in use.",
                "red",
            )
        )
    with open(f"languages/{state.settings.language}.json") as file:
        translations.update(loads(file.read()))
    print(colored(translations["Initialization..."], "light_green"))
    print(colored(translations["Assistant initialization..."], "light_magenta"))
    external_capabilities: dict[str, AssistantFunction] = {}
    for module, module_state in state.settings.modules_states.items():
        if not module_state or not exists(join("modules", module, "__init__.py")):
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
    setattr(server.RequestHandlerClass, "server_phase", "Runtime")
    return state


if __name__ == "__main__":
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
    try:
        with open("prev.data", "rt") as file:
            prev_data: dict[str, Any] = loads(file.read())
            if args.language == "auto":
                args.language = prev_data.get("language", "english")
    except Exception:
        if args.language == "auto":
            args.language = "english"
    if not exists(f"languages/{args.language}.json"):
        print(
            colored(
                f"Translation to language {args.language} "
                "does't exits. The defaults in use.",
                "red",
            )
        )
    with open(f"languages/{args.language}.json") as file:
        translations.update(loads(file.read()))
    server = WebServer(translations=translations, result_config=_calculated_config)
    web_server_thread = Thread(target=server.serve_forever)
    web_server_thread.start()
    with server.lock:
        print(colored("Configuration successfully set.", "light_magenta"))

    state: AppState = init()
    state.voice_handler.record(state=state)
    server.shutdown()
    web_server_thread.join()
