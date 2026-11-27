#!/bin/sh
# Промежуточное представление команд из спецификации УВМ.
set -e
cd "$(dirname "$0")/.."
mkdir -p out
./run.sh examples/spec.json out/spec.bin --test
python3 -m unittest tests.test_assembler -v
