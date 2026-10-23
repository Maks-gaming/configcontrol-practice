#!/bin/sh
# Этап 5: DOT, ASCII-деревья и картинки для трех крейтов и тестов.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
for c in serde_json regex clap; do
    echo "== $c"
    ./run.sh "configs/$c.xml" --image "docs/$c.png"
done
for g in cycle diamond deep; do
    echo "== graphs/$g.txt"
    ./run.sh "configs/test_$g.xml" --image "docs/test_$g.png"
done
