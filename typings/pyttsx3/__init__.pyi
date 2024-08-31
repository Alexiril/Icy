from weakref import WeakValueDictionary
from .engine import Engine

_activeEngines: WeakValueDictionary[str, Engine]


def init(driverName: str | None = None, debug: bool = False) -> Engine: ...
def speak(text: str) -> None: ...
