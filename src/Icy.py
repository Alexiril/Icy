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
from src.Nodes.GPTDialogueSaver import GPTDialogueSaver
from src.Nodes.PrevDataWriter import PrevDataWriter
from src.PhraseProcessor import SimpleIntentionClassifier
from src.ResponseViewer import MessageWindow, PronounceText


def init() -> Init:
    """"""

    audio_processors = ()

    intention_classifier = SimpleIntentionClassifier()
    phrase_processors = (intention_classifier,)

    message_window = MessageWindow()
    pronounce_text = PronounceText()
    viewers = (message_window, pronounce_text)

    quit_node = Quit(None)

    prev_data_writer = PrevDataWriter(None, quit_node)
    quit_node.left = prev_data_writer

    gpt_dialogue_saver = GPTDialogueSaver(None, prev_data_writer)
    prev_data_writer.left = gpt_dialogue_saver

    quit_response = AssistantResponse(None, gpt_dialogue_saver, viewers)
    gpt_dialogue_saver.left = quit_response

    assistant_runner = AssistantRunner(None, None, phrase_processors)

    speech_getter = SpeechGetter(None, assistant_runner, audio_processors)
    assistant_runner.left = speech_getter

    gpt_dialogue_hook = GPTDialogueHook(None, speech_getter)
    speech_getter.left = gpt_dialogue_hook

    assistant_response = AssistantResponse(None, gpt_dialogue_hook, viewers)
    gpt_dialogue_hook.left = assistant_response

    loop = LoopNode(None, assistant_response, quit_response)
    assistant_response.left = loop
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
