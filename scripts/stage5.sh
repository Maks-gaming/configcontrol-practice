#!/bin/sh
# Три примера: унарный минус над вектором длины 7, новый вектор.
set -e
cd "$(dirname "$0")/.."
mkdir -p out
for name in vector1 vector2 vector3; do
    echo "=== $name ==="
    ./run.sh "examples/$name.json" "out/$name.bin"
    ./run.sh run "out/$name.bin" "out/$name-dump.json" 20 36
done
