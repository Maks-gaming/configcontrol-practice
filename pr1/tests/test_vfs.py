"""Тесты загрузки VFS из XML."""

import os
import unittest

from src.shell import Shell
from src.vfs import VfsError, load_vfs, vfs_stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VFS_DIR = os.path.join(ROOT, "vfs")


def vfs_path(name):
    """Вернуть полный путь к тестовой VFS."""
    return os.path.join(VFS_DIR, name)


class LoadVfsTest(unittest.TestCase):
    """Загрузка корректных VFS."""

    def test_minimal(self):
        """Минимальная VFS: один текстовый файл."""
        root = load_vfs(vfs_path("minimal.xml"))
        node = root.children["readme.txt"]
        self.assertFalse(node.is_dir)
        self.assertEqual(node.data.decode("utf-8"), "Минимальная VFS")

    def test_base64_file(self):
        """Двоичный файл декодируется из base64."""
        root = load_vfs(vfs_path("files.xml"))
        self.assertEqual(root.children["data.bin"].data, bytes(range(32)))
        self.assertEqual(root.children["empty.txt"].data, b"")

    def test_deep_tree(self):
        """В глубокой VFS не меньше 3 уровней вложенности."""
        root = load_vfs(vfs_path("deep.xml"))
        reports = (root.children["home"].children["student"]
                   .children["docs"].children["reports"])
        self.assertTrue(reports.is_dir)
        stats = vfs_stats(root)
        self.assertGreaterEqual(stats["depth"], 3)
        self.assertEqual(stats["dirs"], 7)
        self.assertEqual(stats["files"], 8)

    def test_source_not_changed(self):
        """Исходный XML-файл после загрузки не меняется."""
        path = vfs_path("deep.xml")
        with open(path, "rb") as file:
            before = file.read()
        load_vfs(path)
        with open(path, "rb") as file:
            self.assertEqual(file.read(), before)


class VfsErrorTest(unittest.TestCase):
    """Ошибки загрузки VFS."""

    def test_errors(self):
        """Каждый плохой файл дает VfsError с понятным текстом."""
        cases = {
            "no_such_file.xml": "файл не найден",
            "bad_xml.xml": "неверный формат XML",
            "bad_root.xml": "корневой элемент",
            "bad_base64.xml": "base64",
        }
        for name, message in cases.items():
            with self.subTest(name=name):
                with self.assertRaisesRegex(VfsError, message):
                    load_vfs(vfs_path(name))


class ShellVfsTest(unittest.TestCase):
    """Подключение VFS к оболочке и стартовый скрипт этапа 3."""

    def start(self, vfs_name):
        """Запустить оболочку с VFS и скриптом этапа 3 без GUI."""
        shell = Shell()
        lines = []
        script = os.path.join(ROOT, "startup", "stage3.txt")
        shell.start(vfs_path(vfs_name), script,
                    lambda text, ok: lines.append(text))
        return shell, lines

    def test_stage3_script(self):
        """VFS загружается, ошибки скрипта пропускаются."""
        shell, lines = self.start("deep.xml")
        self.assertEqual(lines[0], "VFS loaded: " + vfs_path("deep.xml"))
        self.assertIn("dirs: 7, files: 8", "\n".join(lines))
        self.assertEqual(lines[-1], "ls: args=['/bin']")
        self.assertTrue(shell.running)

    def test_bad_vfs_keeps_default(self):
        """При ошибке загрузки остается пустая VFS по умолчанию."""
        shell, lines = self.start("bad_xml.xml")
        self.assertTrue(lines[0].startswith("error: VFS:"))
        self.assertEqual(shell.vfs_source, "default (empty)")
        self.assertEqual(shell.vfs.children, {})


if __name__ == "__main__":
    unittest.main()
