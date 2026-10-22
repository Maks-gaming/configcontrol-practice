#!/bin/sh
# Запуск инструмента из любой папки, аргументы передаются как есть.
DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$DIR${PYTHONPATH:+:$PYTHONPATH}" exec python3 -m src.main "$@"
