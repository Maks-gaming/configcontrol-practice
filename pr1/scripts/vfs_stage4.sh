#!/bin/sh
# Этап 4: команды ls, cd, whoami, find на VFS vfs/deep.xml.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
./run.sh --vfs vfs/deep.xml --script startup/stage4.txt
