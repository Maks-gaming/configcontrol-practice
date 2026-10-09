#!/bin/sh
# Запуск без параметров и вывод справки по параметрам.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
./run.sh --help
./run.sh
