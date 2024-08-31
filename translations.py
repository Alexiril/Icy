from typing import Iterable, Iterator

from termcolor import colored


class Translations(Iterable[str]):
    def __init__(self) -> None:
        self._translations: dict[str, str] = {}

    def update(self, new_translations: dict[str, str]) -> None:
        self._translations.update(new_translations)

    def __getitem__(self, key: str) -> str:
        if key not in self._translations:
            print(
                colored(
                    f"Phrase '{key}' is not translated to the destination language.",
                    "red",
                )
            )
        return self._translations.get(key, key)

    def __setitem__(self, key: str, value: str) -> None:
        self._translations[key] = value

    def __iter__(self) -> Iterator[str]:
        return iter(self._translations)

    def as_dict(self) -> dict[str, str]:
        return dict(self._translations)


translations: Translations = Translations()
