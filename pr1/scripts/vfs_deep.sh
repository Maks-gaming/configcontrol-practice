#!/bin/sh
# Запуск эмулятора с VFS vfs/deep.xml и стартовым скриптом этапа 3.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
./run.sh --vfs vfs/deep.xml --script startup/stage3.txt
