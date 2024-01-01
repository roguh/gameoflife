from typing import TypedDict
class OutputArgs(TypedDict, total=False):
    delay: float
    color: tuple[int, int, int]


def display(board: list[list[bool]], iterations: int | float, args: OutputArgs) -> None:
    return
