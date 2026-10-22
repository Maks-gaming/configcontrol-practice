#!/bin/sh
# Запуск эмулятора из любой папки, аргументы передаются как есть.
# Интерпретатор: python3, если он реально запускается (в Git Bash
# на Windows это бывает заглушка Microsoft Store), иначе python,
# иначе py -3.
DIR="$(cd "$(dirname "$0")" && pwd)"
if python3 -c "" >/dev/null 2>&1; then
    PY="python3"
elif python -c "" >/dev/null 2>&1; then
    PY="python"
else
    PY="py -3"
fi
export PYTHONPATH="$DIR${PYTHONPATH:+:$PYTHONPATH}"
exec $PY -m src.main "$@"
