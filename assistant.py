from json import JSONEncoder, loads
from os.path import exists
from queue import Queue
from random import choice
from traceback import print_exc as print_traceback
from typing import TYPE_CHECKING, Any, Callable, Iterable

# Too long to make stubs for gpt4all, don't want to.
from gpt4all.gpt4all import GPT4All  # type: ignore
from openai import APIStatusError, OpenAI, Stream
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from termcolor import colored

from assistant_function import AssistantFunction
from exceptions import StopRecording
from settings import Gender
from translations import translations

if TYPE_CHECKING:
    from appstate import AppState


class Assistant:
    name: str = ""
    gender: Gender = "Female"
    voice_key: str = ""
    capabilities: dict[str, AssistantFunction] = {}
    failure: Callable[["AppState"], None] | None = None
    gpt_model: GPT4All
    ai_messages: Queue[ChatCompletionMessageParam]
    current_request: str
    chat_mode: bool
    use_chat: bool
    gpt_info: str

    def __init__(
        self,
        name: str,
        gender: Gender,
        voice_key: str,
        gpt_model: str,
        use_chat: bool,
        gpt_info: str,
        external_capabilities: dict[str, AssistantFunction] = {},
    ) -> None:
        self.name = name
        self.gender = gender
        self.voice_key = voice_key
        self.chat_mode = False
        self.use_chat = use_chat
        self.gpt_info = gpt_info
        self.capabilities = {
            "bye": AssistantFunction(
                [
                    translations["full exit"],
                    translations["full stop"],
                    translations["turn off"],
                ],
                self.task_bye,
            ),
            "activate": AssistantFunction(
                [
                    translations["are you here"],
                    translations["hey"],
                    translations["you hear"],
                    translations["hello"],
                ],
                self.task_activate,
            ),
            "start_chat": AssistantFunction(
                [
                    translations["let's chat"],
                    translations["listen to me"],
                    translations["let's talk"],
                ],
                self.task_start_discussion,
            ),
            "stop_chat": AssistantFunction(
                [
                    translations["stop chat"],
                    translations["stop listening"],
                    translations["enough talking"],
                ],
                self.task_stop_discussion,
            ),
            "forget_chat": AssistantFunction(
                [
                    translations["forget our chat"],
                    translations["forget the dialogue"],
                    translations["forget the discussion"],
                    translations["forget everything"],
                ],
                self.task_forget_chat,
            ),
        }
        self.capabilities.update(external_capabilities)
        for _, value in self.capabilities.items():
            value.keys = [f"{self.name.lower()} {phrase}" for phrase in value.keys]
        self.failure = self.assistant_failure
        self.ai_messages = Queue(50)
        self.gpt_model = GPT4All(model_name=gpt_model, model_path=".models/")
        self.current_request = ""

    def handle_request(self, state: "AppState", request: str) -> None:
        if request == "":
            return
        words: list[str] = request.lower().split(" ")
        if not self.chat_mode and self.name.lower() not in words:
            return
        self.current_request = request
        print(colored(f'{translations["Request:"]} {request}', "blue"))
        task = "chat"
        if len(words) == 1:
            task = "activate"
            if (
                function := self.capabilities.get(
                    "activate", AssistantFunction([], None)
                ).reaction
            ) is not None:
                function(state)
        elif len(words) >= 2:
            for command_end in range(1, len(words) + 1):
                if (
                    task := state.intention_classifier.classify(
                        request=(" ".join(words[:command_end])).strip()
                    )
                ) is not None:
                    if (function := self.capabilities[task].reaction) is not None:
                        function(state, *words)
                    break
            else:
                if self.use_chat:
                    task = "chat"
                    self.task_chat(state, *words)
                elif (function := self.failure) is not None:
                    function(state)
        print(colored(f'{translations["Classified task:"]} {task}', "yellow"))

    def assistant_failure(self, state: "AppState") -> None:
        state.voice_handler.say(
            choice(
                [
                    translations["Can you repeat, please?"],
                    translations["Couldn't understand. What did you say again?"],
                ]
            ),
        )

    def task_activate(self, state: "AppState", *_: Any) -> None:
        state.voice_handler.say(
            choice(
                [
                    translations["I'm listening!"],
                    translations["Yeah?"],
                    translations["I'm here."],
                    translations["Always here for you."],
                    translations["Yes? Do you need any help?"],
                    translations["Here."],
                ]
            ),
        )

    def task_bye(self, state: "AppState", *args: Any) -> None:
        state.voice_handler.say(
            choice(
                [
                    translations["See you next time."],
                    translations["Okay, see you."],
                    translations["Okay, bye!"],
                    translations["Have a good day."],
                ]
            ),
        )
        if len(list(self.ai_messages.queue)) > 0:
            general_data = ""
            for chunk in self.handle_gpt(
                state,
                "Select the most import data from our conversation and "
                "print it as short and detailed as possible.",
                list(self.ai_messages.queue),
                translations[
                    "You are a simple text parser. Don't answer as an assistant. "
                    "Answer exactly how you have to."
                ],
            ):
                if isinstance(chunk, ChatCompletionChunk):
                    chunk = chunk.choices[0].delta.content
                    if chunk is None:
                        break
                general_data += chunk
            config: dict[str, Any] = {}
            if exists("prev.data"):
                with open("prev.data", "rt") as file:
                    config.update(loads(file.read()))
            config["gpt_info"] = general_data
            with open("prev.data", "wt") as file:
                print(JSONEncoder().encode(config), file=file)
        raise StopRecording()

    def task_start_discussion(self, state: "AppState", *args: Any) -> None:
        if not self.use_chat:
            return
        self.chat_mode = True
        state.voice_handler.say(
            choice(
                [
                    translations["Yeah, let's talk!"],
                    translations["I'm here to help."],
                    translations["I love chatting!"],
                    translations["Okay, I'm listening."],
                ]
            ),
        )

    def task_stop_discussion(self, state: "AppState", *args: Any) -> None:
        if not self.use_chat:
            return
        self.chat_mode = False
        state.voice_handler.say(
            translations[
                "Alright. If you need me, just mention my name in your speech."
            ]
        )

    def handle_gpt(
        self,
        state: "AppState",
        request: str,
        history: list[ChatCompletionMessageParam],
        system_prompt: str | None = None,
        add_gpt_info: bool = True,
    ) -> Iterable[str] | Stream[ChatCompletionChunk]:
        history = history.copy()
        bot_name_description = translations[
            "You are a nice friend, not an assistant, your name is"
        ]
        final_command = translations["Answer creative and detailed, but short."]
        history.insert(
            0,
            (
                {
                    "role": "system",
                    "content": (
                        (
                            (
                                f'{bot_name_description} '
                                f'{self.name}. {translations["You are a"]} '
                                f'{translations[self.gender]}. '
                                f'{final_command} '
                            )
                            if system_prompt is None
                            else system_prompt
                        )
                        + f'{translations["You know that:"]
                             if len(self.gpt_info) != 0 else ""} {self.gpt_info}'
                        if add_gpt_info
                        else ""
                    ),
                }
            ),
        )

        def offline_gpt() -> Iterable[str]:
            def gpt_brakes(token_id: int, response: str) -> bool:
                return state.voice_handler.speak_worker.work

            with self.gpt_model.chat_session():
                self.gpt_model._history = history  # type: ignore
                return self.gpt_model.generate(
                    request,
                    max_tokens=1024,
                    temp=1.0,
                    streaming=True,
                    callback=gpt_brakes,
                )

        if not state.settings.use_openai_gpt:
            return offline_gpt()
        try:
            return OpenAI().chat.completions.create(
                model="gpt-4o-mini",
                messages=history + [{"role": "user", "content": request}],
                temperature=1,
                stream=True,
            )
        except APIStatusError:
            print(colored("OpenAI services are unavaliable.", "light_red"))
        except Exception:
            print_traceback()
        return offline_gpt()

    def task_chat(self, state: "AppState", *args: Any) -> None:
        if not self.use_chat:
            return
        state.voice_handler.say(
            choice(
                [
                    translations["Okay, wait a second."],
                    translations["Yeah, let me think."],
                    translations["Oh, okay, wait please."],
                    translations["Well, give me a second."],
                    translations["Oh, well, let me think."],
                    translations["Interesting. Let me think."],
                ]
            ),
        )
        content = " ".join(args)
        result: Iterable[str] | Stream[ChatCompletionChunk] = self.handle_gpt(
            state, content, list(self.ai_messages.queue)
        )
        self.ai_messages.put({"role": "user", "content": content})
        state.assistant.ai_messages.put(
            {
                "role": "assistant",
                "content": state.voice_handler.say(result),
            }
        )

    def task_forget_chat(self, state: "AppState", *args: Any) -> None:
        self.ai_messages = Queue(50)
        open("last.ai.info", "w").close()
        state.voice_handler.say(
            choice(
                [
                    translations["Okay, I have no idea what you are talking about."],
                    translations["Fine, let's forget about it."],
                    translations["Yeah. What else can I help you with?"],
                    translations["Sure, let's skip it."],
                    translations["Yeah, of course. Did we talk about something?"],
                    translations["Alright, if you say so."],
                ]
            ),
        )
