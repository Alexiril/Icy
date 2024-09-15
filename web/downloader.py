from shutil import move
from os import listdir
from requests import get
from pathlib import Path
from vosk import Model


class Downloader():

    def download_vosk_model(model_name) -> None:
        if model_name in listdir(Path(".") / ".models"):
            print(f"{model_name} already exists")
        else:
            Model(model_name=model_name)
            move(Path.home() / f".cache/vosk/{model_name}", Path(".") / ".models")

    def show_downloaded_models() -> str:
        models = ""
        response = get("https://alphacephei.com/vosk/models/model-list.json", timeout=10)
        for model in response.json():
            if model["name"] in listdir(Path(".") / ".models"):
                models += model["name"] + "\n"
        return models
