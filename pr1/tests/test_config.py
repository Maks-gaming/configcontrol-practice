"""Тесты параметров командной строки и стартового скрипта."""

import getpass
import os
import unittest

from src.config import config_lines, parse_args
from src.shell import Shell

DATA = os.path.join(os.path.dirname(__file__), "data")


class ConfigTest(unittest.TestCase):
    """Проверка разбора параметров и отладочного вывода."""

    def test_defaults(self):
        """Без параметров оба пути равны None."""
        config = parse_args([])
        self.assertIsNone(config.vfs)
        self.assertIsNone(config.script)

    def test_all_params(self):
        """Оба параметра разбираются и попадают в отладочный вывод."""
        config = parse_args(["--vfs", "a.xml", "--script=s.txt"])
        lines = config_lines(config)
        self.assertIn("[debug]   vfs = a.xml", lines)
        self.assertIn("[debug]   script = s.txt", lines)


class ScriptTest(unittest.TestCase):
    """Выполнение стартового скрипта без GUI."""

    def run_script(self, name):
        """Выполнить скрипт из tests/data, вернуть (вывод, ошибки)."""
        shell = Shell()
        lines = []
        errors = shell.run_script(os.path.join(DATA, name),
                                  lambda text, ok: lines.append(text))
        return shell, lines, errors

    def test_errors_are_skipped(self):
        """Ошибочные строки сообщаются, выполнение продолжается."""
        _, lines, errors = self.run_script("errors.txt")
        self.assertEqual(errors, 3)
        self.assertTrue(lines[0].endswith("$ cd one"))
        self.assertIn("command not found", lines[3])
        self.assertEqual(lines[-1], getpass.getuser())

    def test_input_is_echoed(self):
        """Каждая команда показывается с приглашением."""
        shell, lines, _ = self.run_script("errors.txt")
        self.assertEqual(lines[0], shell.prompt() + "cd one")

    def test_exit_stops_script(self):
        """После exit оставшиеся строки не выполняются."""
        shell, lines, _ = self.run_script("exit.txt")
        self.assertFalse(shell.running)
        self.assertFalse(any(line.endswith("ls never") for line in lines))

    def test_missing_script(self):
        """Несуществующий скрипт дает сообщение об ошибке."""
        _, lines, errors = self.run_script("no_such_file.txt")
        self.assertEqual(errors, 1)
        self.assertIn("cannot read script", lines[0])


if __name__ == "__main__":
    unittest.main()
