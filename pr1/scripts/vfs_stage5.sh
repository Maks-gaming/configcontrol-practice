#!/bin/sh
# Этап 5: команда rm на VFS vfs/deep.xml (изменения только в памяти).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
./run.sh --vfs vfs/deep.xml --script startup/stage5.txt
