""""""

from copy import copy
from datetime import datetime
from threading import Thread
from tkinter import NSEW, Event, Menu, Misc, Tk
from tkinter.ttk import Label
from typing import Callable
from src import State
from src.Interfaces import ResponseViewerInterface


class MessageWindow(ResponseViewerInterface):
    """"""

    state: State | None
    thread: "MessageWindowThread"
    start_time: datetime

    class MessageWindowThread(Thread):
        def __init__(
            self,
            state: State,
            symbols_per_line: int = 40,
        ) -> None:
            self.symbols_per_line: int = symbols_per_line
            self.state: State = state
            self.root: Tk
            self.popup_menu: Menu
            self.label: Label
            Thread.__init__(self)

        def show_window(self, text: str | Callable[[], str]) -> None:
            self.text: str | Callable[[], str] = text
            self.start()

        def terminate(self) -> None:
            self.root.quit()

        def popup(self, event: "Event[Misc]") -> None:
            try:
                self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.popup_menu.grab_release()

        def run(self) -> None:
            self.root = Tk()
            setattr(self.root, "alpha_delta", 0.1)
            setattr(self.root, "alpha_pause", False)
            self.root.protocol("WM_DELETE_WINDOW", self.terminate)
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            text: str = str(self.text) if type(self.text) is str else ""
            self.label = Label(self.root, text=text)
            self.label.config(
                font=("Segoe UI", 400 // self.symbols_per_line),
                foreground="#222222",
                wraplength=400,
            )
            self.label.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)
            self.label.bind("<Button-1>", self.popup)
            self.popup_menu = Menu(self.root, tearoff=0)
            self.popup_menu.add_command(
                label="Copy text", command=lambda: copy(self.label["text"])
            )

            def stop_command() -> bool:
                return self.terminate() is self.state.update(
                    {"__force_stop_response": True}
                )

            self.popup_menu.add_command(
                label="Force stop",
                command=stop_command,
            )
            self.root.geometry("+10-60")
            self.root.overrideredirect(True)
            self.root.wait_visibility(self.root)
            # value in attributes is Unknown
            self.root.attributes("-alpha", 0.0)  # type: ignore
            self.root.attributes("-topmost", True)  # type: ignore

            def handle_transparency() -> None:
                if getattr(self.root, "alpha_pause"):
                    if not self.state.get("__force_stop_response", False):
                        self.root.after(100, handle_transparency)
                        return
                    setattr(self.root, "alpha_pause", False)
                delta = getattr(self.root, "alpha_delta")
                if self.root.attributes("-alpha") > 0.8 and delta > 0:  # type: ignore
                    delta *= -1
                    setattr(self.root, "alpha_delta", delta)
                    setattr(self.root, "alpha_pause", True)
                    self.root.after(100, handle_transparency)
                    return
                self.root.attributes(  # type: ignore
                    "-alpha",
                    self.root.attributes("-alpha") + delta,  # type: ignore
                )
                if self.root.attributes("-alpha") < 0.1:  # type: ignore
                    self.terminate()
                self.root.after(1000 // 24, handle_transparency)

            self.root.after(1000 // 24, handle_transparency)
            self.root.mainloop()

        def review(self) -> None:
            if isinstance(self.text, Callable):
                text = self.text()
                self.label.config(text=text)

    def __init__(self) -> None:
        self.state = None
        return

    def view(self, text: str) -> None:
        self.thread.show_window(text)

    def hook(self, get_text: Callable[[], str]) -> None:
        self.thread.show_window(get_text)

    def review(self) -> None:
        self.start_time = datetime.now()
        self.thread.review()

    def before_start(self, state: State) -> None:
        self.state = state
        self.thread = MessageWindow.MessageWindowThread(self.state)
        self.start_time = datetime.now()
        return

    def finished(self) -> bool:
        return (datetime.now() - self.start_time).seconds > 5

    def normal_terminate(self) -> None:
        self.thread.terminate()
