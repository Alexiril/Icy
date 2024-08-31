class Voice:
    id: str
    name: str | None
    languages: list[str]
    gender: str | None
    age: int | float | str | None

    def __init__(
        self,
        id: str,
        name: str | None = None,
        languages: list[str] = [],
        gender: str | None = None,
        age: int | float | str | None = None,
    ) -> None: ...
