#!/bin/sh
# Машинный код всех команд из спецификации УВМ.
set -e
cd "$(dirname "$0")/.."
mkdir -p out
./run.sh examples/spec.json out/spec.bin --test
