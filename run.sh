#!/bin/sh
# Запуск инструмента из любой папки, аргументы передаются как есть.
# Работает в Linux, macOS и Git Bash на Windows.
DIR="$(cd "$(dirname "$0")" && pwd)"
# Ищем рабочий Python 3: в Windows python3 бывает заглушкой Store.
if python3 -c "" >/dev/null 2>&1; then
    PY="python3"
elif python -c "import sys; assert sys.version_info[0] == 3" \
        >/dev/null 2>&1; then
    PY="python"
elif py -3 -c "" >/dev/null 2>&1; then
    PY="py -3"
else
    echo "Не найден Python 3 (python3, python или py -3)" >&2
    exit 1
fi
export PYTHONUTF8=1
export PYTHONPATH="$DIR"
exec $PY -m src.main "$@"
