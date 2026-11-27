#!/bin/sh
# Унарный минус для положительного числа и нуля.
set -e
cd "$(dirname "$0")/.."
mkdir -p out
./run.sh examples/neg.json out/neg.bin
./run.sh run out/neg.bin out/neg-dump.json 40 42
