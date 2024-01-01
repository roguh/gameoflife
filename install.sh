#!/bin/sh
set -ex

BIN=/usr/bin/
DATA=/usr/share/gameoflife

cp gameoflife.py gameoflife_screensaver "$BIN"
mkdir -p "$DATA"
cp -r samples/*.txt "$DATA"
sed -i "s#samples#$DATA#" "$BIN/gameoflife_screensaver"
