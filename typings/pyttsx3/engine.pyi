from typing import Any, Callable

class Engine:  # noqa: E302
    def __init__(self, driverName: str | None = None, debug: bool = False) -> None: ...
    def connect[R](  # noqa: E301
        self, topic: str, cb: Callable[..., R]
    ) -> dict[str, str | Callable[..., R]]: ...
    def disconnect(self, token: dict[str, str | Callable[..., Any]]) -> None: ...
    def say(self, text: str, name: str | None = None) -> None: ...
    def stop(self) -> None: ...
    def save_to_file(  # noqa: E301
        self, text: str, filename: str, name: str | None = None
    ) -> None: ...
    def isBusy(self) -> bool: ...
    def getProperty(self, name: str) -> Any: ...
    def setProperty(self, name: str, value: Any) -> None: ...
    def runAndWait(self) -> None: ...
    def startLoop(self, useDriverLoop: bool = True) -> None: ...
    def endLoop(self) -> None: ...
    def iterate(self) -> None: ...
