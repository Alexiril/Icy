from threading import Thread
from tkinter import NSEW, Event, Label, Menu, Misc, Tk
from types import SimpleNamespace
from typing import Callable

from pyperclip import copy


class MessageWindow(Thread):
    def __init__(
        self,
        text: str | Callable[[], str],
        show: Callable[[], bool],
        speak_worker: SimpleNamespace,
        symbols_per_line: int = 40,
    ) -> None:
        self.text: str | Callable[[], str] = text
        self.show: Callable[[], bool] = show
        self.symbols_per_line: int = symbols_per_line
        self.speak_worker: SimpleNamespace = speak_worker
        self.root: Tk
        self.popup_menu: Menu
        Thread.__init__(self)
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
        label = Label(self.root, text=text)
        label.config(
            font=("Segoe UI", 400 // self.symbols_per_line),
            foreground="#222222",
            wraplength=400,
        )
        label.grid(row=0, column=0, sticky=NSEW, padx=10, pady=10)
        label.bind("<Button-1>", self.popup)
        self.popup_menu = Menu(self.root, tearoff=0)
        self.popup_menu.add_command(
            label="Copy text", command=lambda: copy(label["text"])
        )

        def stop_command() -> bool:
            return self.terminate() == setattr(self.speak_worker, "work", False)

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
            if isinstance(self.text, Callable):
                text = self.text()
                label.config(text=text)
            if getattr(self.root, "alpha_pause"):
                if self.show():
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
