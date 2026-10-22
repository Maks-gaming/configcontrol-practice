#!/bin/sh
# Этап 3: граф для всех тестовых репозиториев и ошибки файла графа.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
for g in simple cycle diamond deep; do
    echo "== graphs/$g.txt"
    ./run.sh "configs/test_$g.xml" --show graph
done
for g in bad_line bad_name; do
    echo "== graphs/$g.txt"
    sed "s/test_simple/x/; s#graphs/simple.txt#graphs/$g.txt#" \
        configs/test_simple.xml > /tmp/cargo_graph_bad.xml
    ./run.sh /tmp/cargo_graph_bad.xml --show graph
done
rm -f /tmp/cargo_graph_bad.xml
exit 0
