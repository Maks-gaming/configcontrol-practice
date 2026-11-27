#!/bin/sh
# Копирование массива с адресов 20-22 на адреса 30-32.
set -e
cd "$(dirname "$0")/.."
mkdir -p out
./run.sh examples/copy.json out/copy.bin
./run.sh run out/copy.bin out/copy-dump.json 20 32
