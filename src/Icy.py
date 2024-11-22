"""This module contains Icy default working scheme"""

from src.Nodes import (
    ArgsParser,
    AssistantResponse,
    AssistantRunner,
    AssistantStart,
    GPTDialogueHook,
    Init,
    LoopNode,
    PrevDataReader,
    Quit,
    ResourcesLoader,
    SpeechGetter,
    WebConfig,
    WebHook,
)
from src.PhraseProcessor import IntentionClassifier
from src.ResponseViewer import MessageWindow, PronounceText


def init() -> Init:
    """"""

    audio_processors = ()

    intention_classifier = IntentionClassifier()
    phrase_processors = (intention_classifier,)

    message_window = MessageWindow()
    pronounce_text = PronounceText()
    viewers = (message_window, pronounce_text)

    quit_node = Quit(None)

    quit_response = AssistantResponse(None, quit_node, viewers)
    quit_node.left = quit_response

    assistant_runner = AssistantRunner(None, None, phrase_processors)

    speech_getter = SpeechGetter(None, assistant_runner, audio_processors)
    assistant_runner.left = speech_getter

    assistant_response = AssistantResponse(None, speech_getter, viewers)
    speech_getter.left = assistant_response

    gpt_dialog_hook = GPTDialogueHook(None, assistant_response)
    assistant_response.left = gpt_dialog_hook

    loop = LoopNode(None, gpt_dialog_hook, quit_response)
    gpt_dialog_hook.left = loop
    assistant_runner.right = loop
    quit_response.left = loop

    web_hook = WebHook(None, loop)
    loop.left = web_hook

    assistant_start = AssistantStart(None, web_hook)
    web_hook.left = assistant_start

    resources_loader = ResourcesLoader(None, assistant_start)
    assistant_start.left = resources_loader

    prev_data_reader = PrevDataReader(None, resources_loader)
    resources_loader.left = prev_data_reader

    web_config = WebConfig(None, prev_data_reader)
    prev_data_reader.left = web_config

    args_parser = ArgsParser(None, web_config)
    web_config.left = args_parser

    prev_data_reader = PrevDataReader(None, args_parser)
    args_parser.left = prev_data_reader

    init = Init(prev_data_reader)
    prev_data_reader.left = init

    return init
