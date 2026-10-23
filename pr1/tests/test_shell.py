"""Тесты выполнения команд оболочки."""

import getpass
import os
import unittest

from src.shell import Shell, ShellError
from src.vfs import load_vfs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEEP_VFS = os.path.join(ROOT, "vfs", "deep.xml")
HOME = "/home/maksim"


def make_shell():
    """Оболочка с VFS deep.xml, текущий каталог домашний."""
    shell = Shell(HOME)
    shell.vfs = load_vfs(DEEP_VFS)
    shell.go_home()
    return shell


class ShellTest(unittest.TestCase):
    """Проверка общих правил, exit и ошибок."""

    def __init__(self, method_name="runTest"):
        """Создать новую оболочку для каждого теста.

        unittest создает отдельный объект класса на каждый тест,
        поэтому состояние между тестами не переносится.
        """
        super().__init__(method_name)
        self.shell = make_shell()

    def test_unknown_command(self):
        """Неизвестная команда дает ошибку."""
        with self.assertRaisesRegex(ShellError, "command not found"):
            self.shell.execute("foo bar")

    def test_bad_args(self):
        """Неверные аргументы дают ошибку."""
        bad_lines = ["cd a b", "ls -z", "exit now", 'ls "x']
        for line in bad_lines:
            with self.subTest(line=line):
                text, ok = self.shell.run_line(line)
                self.assertFalse(ok)
                self.assertTrue(text.startswith("error:"))

    def test_exit(self):
        """Команда exit останавливает оболочку."""
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)

    def test_prompt(self):
        """Приглашение содержит user@host и текущий каталог."""
        self.assertIn("@", self.shell.prompt())
        self.assertTrue(self.shell.prompt().endswith(":~$ "))
        self.shell.execute("cd /etc")
        self.assertTrue(self.shell.prompt().endswith(":/etc$ "))

    def test_home_any_user(self):
        """Нет /home/<user>: домашним становится первый каталог /home."""
        shell = Shell("/home/nobody")
        shell.vfs = load_vfs(DEEP_VFS)
        shell.go_home()
        self.assertEqual(shell.cwd, ["home", "maksim"])
        self.assertTrue(shell.prompt().endswith(":~$ "))
        shell.execute("cd ~/docs")
        self.assertTrue(shell.prompt().endswith(":~/docs$ "))

    def test_home_is_root(self):
        """Нет каталога /home: домашний каталог - корень."""
        shell = Shell("/home/nobody")
        shell.vfs = load_vfs(os.path.join(ROOT, "vfs", "files.xml"))
        shell.go_home()
        self.assertEqual(shell.cwd, [])
        self.assertTrue(shell.prompt().endswith(":/$ "))
        self.assertEqual(shell.execute("ls ~"), shell.execute("ls /"))


class LsTest(unittest.TestCase):
    """Команда ls."""

    def __init__(self, method_name="runTest"):
        """Создать новую оболочку для каждого теста.

        unittest создает отдельный объект класса на каждый тест,
        поэтому состояние между тестами не переносится.
        """
        super().__init__(method_name)
        self.shell = make_shell()

    def test_current_dir(self):
        """Без аргументов показан текущий каталог без скрытых."""
        self.assertEqual(self.shell.execute("ls"), "docs")

    def test_hidden(self):
        """С -a видны скрытые файлы, . и .."""
        self.assertEqual(self.shell.execute("ls -a").split(),
                         [".", "..", ".profile", "docs"])

    def test_long(self):
        """С -l видны тип, права и размер."""
        lines = self.shell.execute("ls -l /etc").splitlines()
        self.assertEqual(lines[0].split(), ["-rw-r--r--", "8", "hostname"])
        self.assertTrue(self.shell.execute("ls -l /").startswith("d"))

    def test_paths(self):
        """Относительный, абсолютный путь, .. и ~."""
        self.assertEqual(self.shell.execute("ls /bin"), "hello")
        self.assertEqual(self.shell.execute("ls docs/reports/.."),
                         "plan.txt\nreports")
        self.assertEqual(self.shell.execute("ls ../.."), "bin\netc\nhome\ntmp")
        self.assertEqual(self.shell.execute("ls ~"), "docs")

    def test_file_and_many(self):
        """Файл выводится по имени, у нескольких каталогов заголовки."""
        self.assertEqual(self.shell.execute("ls /etc/motd"), "/etc/motd")
        self.assertEqual(self.shell.execute("ls /bin /tmp"),
                         "/bin:\nhello\n\n/tmp:")

    def test_errors(self):
        """Нет пути, неверная опция."""
        with self.assertRaisesRegex(ShellError, "No such file"):
            self.shell.execute("ls /nope")
        with self.assertRaisesRegex(ShellError, "invalid option"):
            self.shell.execute("ls -x")


class CdTest(unittest.TestCase):
    """Команда cd."""

    def __init__(self, method_name="runTest"):
        """Создать новую оболочку для каждого теста.

        unittest создает отдельный объект класса на каждый тест,
        поэтому состояние между тестами не переносится.
        """
        super().__init__(method_name)
        self.shell = make_shell()

    def cwd(self):
        """Текущий каталог строкой."""
        return "/" + "/".join(self.shell.cwd)

    def test_paths(self):
        """Переходы по разным видам путей."""
        cases = [
            ("cd docs/reports", HOME + "/docs/reports"),
            ("cd ..", HOME + "/docs"),
            ("cd ../../..", "/"),
            ("cd ..", "/"),
            ("cd /etc", "/etc"),
            ("cd ~/docs", HOME + "/docs"),
            ("cd ./reports/../.", HOME + "/docs"),
            ("cd", HOME),
        ]
        for line, expected in cases:
            with self.subTest(line=line):
                self.assertEqual(self.shell.execute(line), "")
                self.assertEqual(self.cwd(), expected)

    def test_errors(self):
        """Нет каталога, это файл, лишние аргументы."""
        cases = {
            "cd /nope": "No such file or directory",
            "cd /etc/motd": "Not a directory",
            "cd / /etc": "too many arguments",
        }
        for line, message in cases.items():
            with self.subTest(line=line):
                with self.assertRaisesRegex(ShellError, message):
                    self.shell.execute(line)
                self.assertEqual(self.cwd(), HOME)


class WhoamiFindTest(unittest.TestCase):
    """Команды whoami и find."""

    def __init__(self, method_name="runTest"):
        """Создать новую оболочку для каждого теста.

        unittest создает отдельный объект класса на каждый тест,
        поэтому состояние между тестами не переносится.
        """
        super().__init__(method_name)
        self.shell = make_shell()

    def test_whoami(self):
        """whoami выводит имя пользователя ОС."""
        self.assertEqual(self.shell.execute("whoami"), getpass.getuser())
        with self.assertRaisesRegex(ShellError, "extra operand"):
            self.shell.execute("whoami root")

    def test_find_all(self):
        """Без шаблона выводится все дерево от пути."""
        self.assertEqual(self.shell.execute("find /etc").splitlines(),
                         ["/etc", "/etc/hostname", "/etc/motd"])
        self.shell.execute("cd docs/reports")
        self.assertEqual(self.shell.execute("find").splitlines()[:2],
                         [".", "./stage1.txt"])

    def test_find_name(self):
        """Поиск по шаблону -name, путь с ~."""
        self.assertEqual(
            self.shell.execute('find / -name "h*"').splitlines(),
            ["/bin/hello", "/etc/hostname", "/home"])
        found = self.shell.execute("find ~ -name stage?.txt").splitlines()
        self.assertEqual(len(found), 3)
        self.assertTrue(found[0].startswith(HOME + "/docs/reports/"))
        self.assertEqual(self.shell.execute("find / -name nothing"), "")

    def test_find_errors(self):
        """Нет пути, нет шаблона, неизвестный предикат."""
        cases = {
            "find /nope": "No such file",
            "find / -name": "missing argument",
            "find / -type f": "unknown predicate",
        }
        for line, message in cases.items():
            with self.subTest(line=line):
                with self.assertRaisesRegex(ShellError, message):
                    self.shell.execute(line)


if __name__ == "__main__":
    unittest.main()
