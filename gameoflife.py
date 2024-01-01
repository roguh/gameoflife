#!/usr/bin/env python3
"""The Game of Life."""
import argparse
import string
import subprocess
import time
from typing import Literal

# pylint: disable=missing-function-docstring, invalid-name

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
    for y in range(len(board)):
        new_row = empty_row()
        other_row = other[y] if y < len(other) else empty_row()
        for x in range(len(board)):
            new_row.append(operator(board[y][x], ix(other_row, x)))
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
        output.append([LIVE if cell in live else DEAD for cell in row])
    assert all(len(row) > 0 for row in output), "no empty rows"
    return output


def cli_loop(
    board: Board,
    name: str | None=None,
    source: str="unknown",
    max_iterations: int | float = float("inf"),
    delay: float = 0.1,
    surface: Surface = surfaces[0],
    pretty: bool = False,
    narrow: bool = False,
    color: bool = False,
) -> None:
    alphabet = (LIVE_STR, DEAD_STR)
    if pretty:
        alphabet = (LIVE_STR_PRETTY, DEAD_STR_PRETTY)
    if narrow:
        alphabet = (alphabet[0][0], alphabet[1][0])

    if max_iterations == 0:
        print(show(board, alphabet))

    iterations = 0
    while iterations < max_iterations:
        # Update
        board = update(board, surface=surface)

        # Display
        if color:
            print(A_RED_BOLD)
        print(show(board, alphabet))
        if color:
            print(A_RESET_COLOR)
        if all(not cell for row in board for cell in row):
            print("empty board")
        print("Game of Life", iterations)
        print(name, "source:", source)
        iterations += 1
        if iterations < max_iterations:
            time.sleep(delay)
            print(A_CLEAR, end=A_TOP)


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
    parser.add_argument("--source", default="gameoflife written in python")
    parser.add_argument("--name", default=None)
    parser.add_argument("--pretty", "-p", action="store_true")
    parser.add_argument("--narrow", "-n", action="store_true")
    parser.add_argument("--color", "-c", action="store_true")
    parser.add_argument(
        "--size",
        type=int,
        default=None,
        help="If a file is not given, how big should the board be? The size of the terminal window may be used.",
    )
    board_input = parser.add_mutually_exclusive_group(required=True)
    board_input.add_argument(
        "--file",
        "-f",
        help=f"Dead cells and live cells are represented by the characters {DEAD_STR} and {LIVE_STR}",
    )
    board_input.add_argument("BOARD", nargs="?")
    board_input.add_argument("--empty-board", action="store_true")
    board_input.add_argument("--glider-board", action="store_true")

    args = parser.parse_args()

    size = args.size
    if not size:
        # Use terminal width to find size
        try:
            width = int(subprocess.check_output(['tput','cols']))
            height = int(subprocess.check_output(['tput','lines']))
            size = min(width, height)
            # For additional output
            size -= 3
        except:
            size = 32
            print("Unable to find terminal size with Linux tput")
    if args.empty_board:
        init_board = empty(size, size)
    elif args.file:
        with open(args.file, encoding="utf-8") as boardfile:
            init_board = parse(boardfile.readlines())
    else:
        top = 2
        offset = 8
        init_board = empty(size, size)
        direction = True
        for y in range(top, size, offset):
            init_board = add(
                init_board,
                shift(glider(up=direction, left=direction), x=size // 2, y=y),
            )
            direction = not direction
    try:
        cli_loop(
            board=init_board,
            max_iterations=args.iterations,
            source=args.source,
            delay=args.delay,
            surface=args.surface,
            pretty=args.pretty,
            narrow=args.narrow,
            color=args.color,
        )
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
