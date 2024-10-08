from typing import Any, Callable, Literal

class PyperclipException(RuntimeError): ...

class PyperclipWindowsException(PyperclipException):
    def __init__(self, message: str) -> None: ...

class PyperclipTimeoutException(PyperclipException): ...

def init_osx_pbcopy_clipboard() -> tuple[Callable[..., None], Callable[[], str]]: ...
def init_osx_pyobjc_clipboard() -> tuple[Callable[..., None], Callable[[], Any]]: ...
def init_qt_clipboard() -> tuple[Callable[..., None], Callable[[], str | Any]]: ...
def init_xclip_clipboard() -> tuple[Callable[..., None], Callable[..., str]]: ...
def init_xsel_clipboard() -> tuple[Callable[..., None], Callable[..., str]]: ...
def init_wl_clipboard() -> tuple[Callable[..., None], Callable[..., str]]: ...
def init_klipper_clipboard() -> tuple[Callable[..., None], Callable[[], str]]: ...
def init_dev_clipboard_clipboard() -> tuple[Callable[..., None], Callable[[], str]]: ...

class ClipboardUnavailable: ...

def init_no_clipboard() -> tuple[ClipboardUnavailable, ClipboardUnavailable]: ...

class CheckedCall:
    def __init__(self, f: Callable[..., Any]) -> None: ...
    def __call__(self, *args: Any) -> Any: ...
    def __setattr__(self, key: str, value: Any) -> None: ...

def init_windows_clipboard() -> (
    tuple[Callable[..., None], Callable[[], str | None]]
): ...
def init_wsl_clipboard() -> tuple[Callable[..., None], Callable[[], str]]: ...
def determine_clipboard() -> (
    tuple[Callable[..., None], Callable[[], str]]
    | tuple[Callable[..., None], Callable[..., str]]
    | tuple[ClipboardUnavailable, ClipboardUnavailable]
): ...

clipboard_type = Literal[
    "pbcopy",
    "pyobjc",
    "qt",
    "xclip",
    "xsel",
    "wl-clipboard",
    "klipper",
    "windows",
    "no",
]

def set_clipboard(clipboard: clipboard_type) -> None: ...
def lazy_load_stub_copy(text: str) -> None: ...
def lazy_load_stub_paste() -> str: ...
def is_available() -> bool: ...

copy: Callable[[str], None]
paste: Callable[[], str]
