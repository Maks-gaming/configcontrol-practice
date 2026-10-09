#!/bin/sh
# Только стартовый скрипт: рабочий и несуществующий.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
./run.sh --script startup/stage2.txt
./run.sh --script startup/no_such_script.txt
