"""Тесты команды rm (этап 5)."""

import os
import unittest

from src.shell import Shell, ShellError
from src.vfs import get_node, load_vfs, split_path, vfs_stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEEP_VFS = os.path.join(ROOT, "vfs", "deep.xml")


class RmTest(unittest.TestCase):
    """Удаление файлов и каталогов в памяти."""

    def __init__(self, method_name="runTest"):
        """Оболочка с VFS deep.xml в домашнем каталоге.

        unittest создает отдельный объект класса на каждый тест,
        поэтому удаления одного теста не видны в другом.
        """
        super().__init__(method_name)
        self.shell = Shell("/home/maksim")
        self.shell.vfs = load_vfs(DEEP_VFS)
        self.shell.go_home()

    def exists(self, path):
        """Есть ли узел по абсолютному пути."""
        parts = split_path([], path, [])
        return get_node(self.shell.vfs, parts) is not None

    def test_remove_files(self):
        """Файлы удаляются по относительному, абсолютному пути и ~."""
        self.shell.execute("rm docs/plan.txt /etc/motd ~/.profile")
        for path in ["/home/maksim/docs/plan.txt", "/etc/motd",
                     "/home/maksim/.profile"]:
            self.assertFalse(self.exists(path))
        self.assertTrue(self.exists("/etc/hostname"))

    def test_remove_dir(self):
        """Каталог удаляется только с -r, вместе с содержимым."""
        with self.assertRaisesRegex(ShellError, "Is a directory"):
            self.shell.execute("rm docs")
        self.assertTrue(self.exists("/home/maksim/docs"))
        self.shell.execute("rm -r docs")
        self.assertFalse(self.exists("/home/maksim/docs"))
        self.assertEqual(vfs_stats(self.shell.vfs)["files"], 4)

    def test_remove_cwd(self):
        """После удаления текущего каталога переход в родительский."""
        self.shell.execute("cd ~/docs/reports")
        self.shell.execute("rm -r /home/maksim/docs")
        self.assertEqual(self.shell.cwd, ["home", "maksim"])

    def test_errors(self):
        """Ошибки: нет операнда, нет пути, корень, '.', опции."""
        cases = {
            "rm": "missing operand",
            "rm /nope": "No such file or directory",
            "rm /": "Is a directory",
            "rm -r /": "dangerous",
            "rm -r .": "refusing",
            "rm -r ../": "refusing",
            "rm -f docs": "invalid option",
        }
        for line, message in cases.items():
            with self.subTest(line=line):
                with self.assertRaisesRegex(ShellError, message):
                    self.shell.execute(line)
        self.assertEqual(vfs_stats(self.shell.vfs)["files"], 8)

    def test_source_not_changed(self):
        """XML-файл VFS после rm -r не меняется."""
        with open(DEEP_VFS, "rb") as file:
            before = file.read()
        self.shell.execute("rm -r /home /etc /bin")
        with open(DEEP_VFS, "rb") as file:
            self.assertEqual(file.read(), before)

    def test_stage5_script(self):
        """Скрипт этапа 5: 8 ошибок, в VFS остались 3 файла."""
        shell = Shell("/home/maksim")
        lines = []
        script = os.path.join(ROOT, "startup", "stage5.txt")
        shell.start(DEEP_VFS, script, lambda text, ok: lines.append(text))
        errors = [line for line in lines if ": error: " in line]
        self.assertEqual(len(errors), 8)
        self.assertIn("dirs: 5, files: 3", lines[-1])


if __name__ == "__main__":
    unittest.main()
