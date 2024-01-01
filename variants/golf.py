#!/usr/bin/env python3
"""The Game of Life, reduced size.



The universe of the Game of Life is a grid of square cells, each of which is either alive ("#") or dead ("."). Every cell interacts with its eight neighbours, which are the cells that are horizontally, vertically, or diagonally adjacent. At each step in time, the following transitions occur:

    Any dead cell with exactly three live neighbours becomes a live cell.
    All other dead cells stay dead.
    Any live cell with two or three live neighbours survives.
    All other live cells die.

Given a 32×32 grid, output the state in the next step. Assume that every cell outside the grid is dead. 


This file contains a well-formatted versin of my original solution (236 bytes):

import sys;B=sys.argv[1].replace('\n','')
X=lambda x:0<=x<1024 and B[x]
for i in range(1024):
 N=[X(i-32),X(i+32),X(i-1),X(i+1),X(i+31),X(i-33),X(i+33),X(i-31)].count("#");print(N==3 and"#"or N==2 and B[i]or".",end=i%32==31 and"\n"or"")
"""
import sys

B = sys.argv[1].replace("\n", "")
X = lambda x: 0 <= x < 1024 and B[x]
for i in range(1024):
    N = [
        X(i - 32),
        X(i + 32),
        X(i - 1),
        X(i + 1),
        X(i + 31),
        X(i - 33),
        X(i + 33),
        X(i - 31),
    ].count("#")
    print(N == 3 and "#" or N == 2 and B[i] or ".", end=i % 32 == 31 and "\n" or "")
