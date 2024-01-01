#!/usr/bin/env python3
"""The Game of Life."""
import argparse
import string
import subprocess
import time
from typing import Callable, Literal, TypedDict

# pylint: disable=missing-class-docstring, missing-function-docstring, invalid-name

Cell = bool
Row = list[bool]
Board = list[list[bool]]
Surface = Literal["sphere", "rectangle", "infinite", "torus", "?"]

LIVE = True
DEAD = False
L = LIVE
D = DEAD

LIVE_STR = "# "
DEAD_STR = "  "
LIVE_STR_PRETTY = "█▒"
DEAD_STR_PRETTY = "  "


class OutputArgs(TypedDict, total=False):
    source: str
    name: str
    delay: float
    pretty: bool
    narrow: bool
    color: tuple[int, int, int]


def empty_row() -> Row:
    return []


surfaces: list[Surface] = ["sphere", "rectangle", "infinite", "torus", "?"]

A_CLEAR = "\033[2J"
A_TOP = "\033[H"
A_RED_BOLD = "\x1b[1;31m"
A_RESET_COLOR = "\x1b[0m"


def ix(row: Row, x: int, default=DEAD) -> Cell:
    return row[x] if 0 <= x < len(row) else default


def empty(width: int, height: int) -> Board:
    return [[DEAD for _ in range(width)] for _ in range(height)]


def glider(up: bool, left: bool) -> Board:
    out = [
        [D, L, D],
        [L, L, D],
        [L, D, L],
    ]
    if not up:
        out.reverse()
    if not left:
        for row in out:
            row.reverse()
    return out


def add(board: Board, other: Board, operator=bool.__or__) -> Board:
    new = []
    for y, row in enumerate(board):
        new_row = empty_row()
        other_row = other[y] if y < len(other) else empty_row()
        for x, cell in enumerate(row):
            new_row.append(operator(cell, ix(other_row, x)))
        new.append(new_row)
    return new


def shift(board: Board, y: int = 0, x: int = 0) -> Board:
    for _ in range(abs(y)):
        if y > 0:
            board.insert(0, [DEAD for _ in range(len(board[0]))])
        if y < 0:
            board.append([DEAD for _ in range(len(board[-1]))])
    for row in board:
        for _ in range(x):
            if x > 0:
                row.insert(0, DEAD)
            if x < 0:
                row.append(DEAD)
    return board


def neighbors(x: int, row: Row, prev_row: Row, next_row: Row, surface: Surface) -> int:
    """Count living neighbors diagonally, horizontally, and vertically."""
    if surface == "sphere":
        return [
            # Wrap around to end of row
            ix(row, x - 1, row[-1]),
            # Wrap around to beginning of row
            ix(row, x + 1, row[0]),
            # Next: wrap around diagonal if at beginning or end
            ix(next_row, x - 1, next_row[-1]),
            # This next_row is always a valid row, handled by the parent function
            ix(next_row, x),
            ix(next_row, x + 1, next_row[0]),
            # Previous: wrap around diagonal if at beginning or end
            ix(prev_row, x - 1, prev_row[-1]),
            # This prev_row is always a valid row, handled by the parent function
            ix(prev_row, x),
            ix(prev_row, x + 1, prev_row[0]),
        ].count(LIVE)
    return [
        ix(row, x - 1),
        ix(row, x + 1),
        ix(next_row, x - 1),
        ix(next_row, x),
        ix(next_row, x + 1),
        ix(prev_row, x - 1),
        ix(prev_row, x),
        ix(prev_row, x + 1),
    ].count(LIVE)


def update(board: Board, surface: Surface) -> Board:
    new_board = []
    prev_row = empty_row()
    if surface == "sphere":
        prev_row = board[-1]
    for y, row in enumerate(board):
        next_row = board[y + 1] if 0 <= y + 1 < len(board) else empty_row()
        if surface == "sphere" and y + 1 == len(board):
            next_row = board[0]
        new_row = empty_row()
        for x, cell in enumerate(row):
            neighbor_count = neighbors(x, row, prev_row, next_row, surface)
            new_row.append(
                LIVE if neighbor_count == 3 else cell if neighbor_count == 2 else DEAD
            )
        new_board.append(new_row)
        prev_row = row
    return new_board


def show(board: Board, alphabet: tuple[str, str] = (LIVE_STR, DEAD_STR), sep="") -> str:
    live, dead = alphabet
    return "\n".join(sep.join(live if cell else dead for cell in row) for row in board)


def parse(lines: list[str], live: str = "#@&" + string.ascii_uppercase) -> Board:
    output: Board = []
    for row in lines:
        row = row.strip()
        if len(row) == 0:
            continue
        output.append([LIVE if cell in live else DEAD for cell in row])
    assert len(output) > 0, f"empty board parsed:\n{lines}"
    assert all(len(row) > 0 for row in output), f"empty rows found:\n{lines}"
    return output


def pick_updater(source: str, surface: Surface) -> Callable[[Board], Board]:
    def command(board_str: str) -> list[str]:
        if source.endswith(".py"):
            return ["python3", source, board_str]
        if source.endswith(".bin"):
            return [source, board_str]
        return ["echo", "Unknown source"]

    def external(board: Board) -> Board:
        # if surface != 'rectangle':
        # logger.warning("Warning: ignoring surface argument for source", source)
        encoded_board = show(board, alphabet=("#", "."))
        output = subprocess.check_output(command(encoded_board)).decode("utf-8")
        # logger.info(output)
        return parse(output.split("\n"))

    def default(board: Board) -> Board:
        return update(board, surface=surface)

    if source.startswith("./variants"):
        print("Using external script", source)
        return external
    return default


def cli_display(board, iteration: int | float, args: OutputArgs) -> None:
    alphabet = (LIVE_STR, DEAD_STR)
    if args.get("pretty"):
        alphabet = (LIVE_STR_PRETTY, DEAD_STR_PRETTY)
    if args.get("narrow"):
        alphabet = (alphabet[0][0], alphabet[1][0])

    # Display
    if args.get("color"):
        print(A_RED_BOLD)
    print(show(board, alphabet))
    if args.get("color"):
        print(A_RESET_COLOR)
    if all(not cell for row in board for cell in row):
        print("empty board")
    print("Game of Life", iteration)
    print(args.get("name", ""), "source:", args.get("source", "unknown"))

    if iteration > 1:
        time.sleep(args.get("delay", 1.0))
        print(A_CLEAR, end=A_TOP)


def loop(
    board: Board,
    max_iterations: int | float = float("inf"),
    surface: Surface = surfaces[0],
    args: OutputArgs | None = None,
) -> None:
    if not args:
        args = {}

    iteration = 0
    if max_iterations == 0:
        cli_display(show(board), iteration, args)

    update_function = pick_updater(args.get("source", "unknown"), surface)

    display = cli_display
    while iteration < max_iterations:
        # Update
        board = update_function(board)

        iteration += 1
        display(board, iteration, args)

def make_init_board(args) -> Board:
    # Use terminal width to find size
    try:
        width = args.width or int(subprocess.check_output(["tput", "cols"]))
        height = args.height or int(subprocess.check_output(["tput", "lines"]))
        height -= 3
        if not args.narrow:
            width //= 2
    except:  # pylint: disable=bare-except
        width, height = 32, 32
        print("Unable to find terminal size with Linux tput")
    if args.empty_board:
        return empty(width, height)
    if args.file:
        with open(args.file, encoding="utf-8") as boardfile:
            return parse(boardfile.readlines())
    if args.glider_board:
        if width > height:
            width = height * (width // height)
        else:
            height = width * (height // width)
    top = 2
    offset = 8
    board = empty(width, height)
    direction = True
    for y in range(top, height, offset):
        board = add(
            board,
            shift(glider(up=direction, left=direction), x=width // 2, y=y),
        )
        direction = not direction
    return board

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--iterations", "-i", type=int, default=float("inf"))
    parser.add_argument("--delay", "-d", type=float, default=0.03)
    parser.add_argument(
        "--surface",
        "-s",
        default=surfaces[0],
        choices=surfaces,
        help="The shape of the universe.",
    )
    parser.add_argument(
        "--source",
        choices=["this", "./variants/golf.py"],
        default="gameoflife written in python",
    )
    parser.add_argument("--name", default="")
    parser.add_argument("--pretty", "-p", action="store_true")
    parser.add_argument("--narrow", "-n", action="store_true")
    parser.add_argument("--color", "-c", action="store_true")
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=None,
        help="Minimum size of the board. "
        "The size of the terminal window may be used if this option not given.",
    )
    parser.add_argument(
        "--height", "-l",
        type=int,
        default=None,
        help="Minimum size of the board. "
        "The size of the terminal window may be used if this option not given.",
    )
    board_input = parser.add_mutually_exclusive_group(required=True)
    board_input.add_argument(
        "--file",
        "-f",
        help="Dead cells and live cells are represented by "
        f"the characters {DEAD_STR} and {LIVE_STR}",
    )
    board_input.add_argument("BOARD", nargs="?")
    board_input.add_argument("--empty-board", action="store_true")
    board_input.add_argument("--glider-board", action="store_true")

    args = parser.parse_args()

    init_board = make_init_board(args)

    output_args: OutputArgs = {
        "name": args.name,
        "source": args.source,
        "delay": float(args.delay),
        "pretty": bool(args.pretty),
        "narrow": bool(args.narrow),
        "color": (255, 0, 0) if args.color else (0, 0, 0),
    }
    try:
        loop(
            board=init_board,
            max_iterations=args.iterations,
            surface=args.surface,
            args=output_args,
        )
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
