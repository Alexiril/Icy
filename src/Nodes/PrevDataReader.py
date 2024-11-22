""""""

from src import Node, State, load_prev


class PrevDataReader(Node):
    """"""

    def __init__(self, left: Node | None, right: Node | None) -> None:
        super().__init__("Previous data file reader", left, right)

    def __call__(self, state: State) -> None:
        try:
            settings = load_prev()
        except Exception as e:
            self.log_error(e)
            settings = {}
        if "settings" not in state:
            state["settings"] = {}
        state["settings"].update(settings)
        return
