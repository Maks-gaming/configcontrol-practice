"""Тесты выполнения команд оболочки."""

import unittest

from src.shell import Shell, ShellError


class ShellTest(unittest.TestCase):
    """Проверка команд-заглушек, exit и ошибок."""

    def setUp(self):
        """Создать новую оболочку для каждого теста."""
        self.shell = Shell()

    def test_ls_stub(self):
        """ls выводит свое имя и аргументы."""
        self.assertEqual(self.shell.execute("ls -la /tmp"),
                         "ls: args=['-la', '/tmp']")

    def test_cd_stub(self):
        """cd выводит свое имя и аргумент."""
        self.assertEqual(self.shell.execute("cd /home"),
                         "cd: args=['/home']")

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
        """exit останавливает оболочку."""
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)

    def test_prompt_has_user_and_host(self):
        """Приглашение содержит username@hostname."""
        self.assertIn("@", self.shell.prompt())


if __name__ == "__main__":
    unittest.main()
