""""""

from pathlib import Path

# Don't have stubs for gpt4all
from gpt4all import GPT4All as _GPT4All  # type: ignore

from src.Interfaces import GPTInterface


class GPT4All(GPTInterface):
    """"""

    @staticmethod
    def gpt4all_model_loader(model_name: str) -> _GPT4All:
        # Auto downloading is something...
        return _GPT4All(model_name=model_name, model_path=Path(".") / ".models")
