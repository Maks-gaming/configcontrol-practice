#!/bin/sh
# Ошибки загрузки VFS: нет файла, битый XML, чужой корень, плохой base64.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
for VFS in vfs/no_such_file.xml vfs/bad_xml.xml vfs/bad_root.xml \
        vfs/bad_base64.xml; do
    ./run.sh --vfs "$VFS" --script startup/stage3.txt
done
