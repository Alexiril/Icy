"""This module contains the Translations class, that is used to contain and pass the
translation map."""

from typing import Iterable, Iterator

from termcolor import colored


class Translations(Iterable[str]):
    """This class contains translated strings and handles cases when there are no
    translation created for a string."""

    def __init__(self) -> None:
        self._translations: dict[str, str] = {}

    def update(self, new_translations: dict[str, str]) -> None:
        """Updates translations dictionary. The new values overwrite the old ones."""

        self._translations.update(new_translations)

    def __getitem__(self, key: str) -> str:
        """Gets the translation for the string. If there are no translation provided,
        returns the original string."""

        if key not in self._translations:
            print(
                colored(
                    f"Phrase '{key}' is not translated to the destination language.",
                    "red",
                )
            )
        return self._translations.get(key, key)

    def __setitem__(self, key: str, value: str) -> None:
        """Changes the translated value of one exact string."""

        self._translations[key] = value

    def __iter__(self) -> Iterator[str]:
        return iter(self._translations)

    def as_dict(self) -> dict[str, str]:
        """Returns the translations as a dictionary (new dict, not a reference)."""

        return dict(self._translations)


translations: Translations = Translations()
