#!/bin/sh
# Запуск ассемблера из любой папки.
DIR="$(cd "$(dirname "$0")" && pwd)"
if python3 -c "" >/dev/null 2>&1; then
    PY="python3"
elif python -c "import sys; assert sys.version_info[0] == 3" \
    >/dev/null 2>&1; then
    PY="python"
elif py -3 -c "" >/dev/null 2>&1; then
    PY="py -3"
else
    echo "Не найден Python 3" >&2
    exit 1
fi
export PYTHONUTF8=1
export PYTHONPATH="$DIR"
if [ "${1:-}" = "run" ]; then
    shift
    exec $PY -m src.interpreter "$@"
fi
exec $PY -m src.assembler "$@"
