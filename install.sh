#!/bin/sh
# Local install with:
# DATA=$HOME/.local/share BIN=$HOME/.local/bin ./install.sh  
# Global install with:
# sudo ./install.sh
set -ex

BIN="${BIN:-/usr/bin/}"
DATA="${DATA:-/usr/share/gameoflife}"

cp gameoflife.py gameoflife_screensaver "$BIN"
mkdir -p "$DATA"
cp -r samples/*.txt "$DATA"
sed -i "s#samples#$DATA#" "$BIN/gameoflife_screensaver"
