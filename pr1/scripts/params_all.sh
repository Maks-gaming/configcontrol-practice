#!/bin/sh
# Все параметры сразу, в обеих формах записи.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
./run.sh --vfs vfs/minimal.xml --script startup/stage2.txt
./run.sh --vfs=vfs/minimal.xml --script=startup/stage2.txt
