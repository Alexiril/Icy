from json import JSONEncoder, loads
from os import listdir
from os.path import isdir, isfile, join
from re import Pattern
from re import compile as re_compile
from re import findall

from termcolor import colored

# https://regex101.com/r/eAeKM6/1
translate_pattern: Pattern[str] = re_compile(
    r"translations *\[[^\"\]]*\"([^\"]+)\"[^\]]*]"
)


def handle_file(path: str, phrases: set[str]) -> None:
    with open(path, "rt") as file:
        print(f"File {path}: ", end="")
        try:
            text: str = file.read()
            print(colored("done", "green"))
        except UnicodeDecodeError:
            print(colored("not text", "red"))
            return
        for phrase in findall(translate_pattern, text):
            phrases.add(phrase)


def handle_folder(path: str, phrases: set[str]) -> None:
    for subpath in listdir(path):
        if isdir((new_path := join(path, subpath))) and \
            subpath[0] != "." and subpath != '__pycache__' and \
            not (subpath == 'modules' and path == '.'):
            handle_folder(path=new_path, phrases=phrases)
        elif isfile(new_path):
            handle_file(path=new_path, phrases=phrases)


def main() -> None:
    phrases: set[str] = set()
    handle_folder(".", phrases)
    result = {s: s for s in sorted(phrases)}
    result["lang_id"] = "en"
    result["lang_name"] = "english"
    with open(join("languages", "english.json"), "wt") as file:
        print(JSONEncoder().encode(result), file=file)
    print(colored("--- English done ---", "light_magenta"))
    for path in listdir("languages"):
        print(f"Language {path}...", end="")
        if path == "english.json":
            print(colored("done", "green"))
            continue
        if not isfile(new_path := join("languages", path)):
            print(colored("not done", "red"))
            continue
        with open(new_path, 'rt') as file:
            try:
                old_translation: dict[str, str] = loads(file.read())
            except UnicodeDecodeError:
                print(colored("not done", "red"))
                continue
        new_translation: dict[str, str] = {key: old_translation.get(key, key) for key in result}
        with open(new_path, 'wt') as file:
            print(JSONEncoder(ensure_ascii=False).encode(new_translation), file=file)
        print(colored("done", "green"))


if __name__ == "__main__":
    main()
