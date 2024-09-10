from typing import Any, Literal

# Yeah, there probably will be more...
Gender = Literal["Female", "Male"]

# Automatic translation builder purposes only
# translations["Female"]
# translations["Male"]

OpenAITTSVoice = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
"""Voices which are avaliable for use with OpenAI TTS API."""


class Settings:
    """Class Settings contains all the properties used in the assistant.
    Also, it's being used to pass the parameters from the configuration
    web page to the bot."""
    language: str = "english"
    assistant_name: str = "Assistant"
    assistant_gender: Gender = "Female"
    assistant_voice_key: str = "Zira"
    assistant_voice_rate: int = 200
    vosk_model: str = ""
    vosk_debug: bool = False
    use_chat: bool = True
    gpt_model: str = ""
    use_openai_gpt: bool = True
    use_openai_tts: bool = False
    openai_tts_model: OpenAITTSVoice = "nova"
    gpt_info: str = ""
    modules_states: dict[str, bool] = {}
    intention_best_proba: float = 0.5

    def __init__(self, calculated_config: dict[str, Any]) -> None:
        for attr in dir(self):
            if attr[0] == "_":
                continue
            value: Any = calculated_config.get(attr, getattr(self, attr))
            # Have no idea how to make it work without Unknown type.
            actual_type: type[Any] = type(getattr(self, attr))  # type: ignore
            if actual_type is not str and type(value) is not actual_type:
                if actual_type is bool:
                    value = value.lower() == "true"
                else:
                    value = actual_type(value)
            setattr(self, attr, value)
