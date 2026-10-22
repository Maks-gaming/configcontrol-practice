#!/bin/sh
# Этап 1: обработка ошибок для всех параметров конфигурации.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
./run.sh configs/missing.xml
for f in configs/bad/*.xml; do
    echo "== $f"
    ./run.sh "$f"
done
exit 0
