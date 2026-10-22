#!/bin/sh
# Этап 4: порядок загрузки для тестовых графов и реальных крейтов.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
for g in simple cycle diamond deep; do
    echo "== graphs/$g.txt"
    ./run.sh "configs/test_$g.xml" --show order
done
for c in serde_json rand; do
    echo "== $c"
    ./run.sh "configs/$c.xml" --show order
done
