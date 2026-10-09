"""Тесты парсера командной строки."""

import os
import unittest
from unittest import mock

from src.parser import ParseError, expand_vars, parse_line


class ParserTest(unittest.TestCase):
    """Проверка раскрытия переменных и разбиения на слова."""

    def test_simple_words(self):
        """Строка делится по пробелам."""
        self.assertEqual(parse_line("ls -l  /home"), ["ls", "-l", "/home"])

    def test_empty_line(self):
        """Пустая строка дает пустой список."""
        self.assertEqual(parse_line("   "), [])

    def test_quotes(self):
        """Аргумент в кавычках остается одним словом."""
        self.assertEqual(parse_line('cd "my dir"'), ["cd", "my dir"])

    @mock.patch.dict(os.environ, {"HOME": "/home/test"})
    def test_expand_home(self):
        """Работают обе формы: $HOME и ${HOME}."""
        self.assertEqual(expand_vars("$HOME ${HOME}/x"),
                         "/home/test /home/test/x")

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_unknown_var_is_empty(self):
        """Неизвестная переменная заменяется пустой строкой."""
        self.assertEqual(parse_line("cd $NO_SUCH_VAR"), ["cd"])

    def test_unclosed_quote(self):
        """Незакрытая кавычка дает ошибку разбора."""
        with self.assertRaises(ParseError):
            parse_line('ls "abc')


if __name__ == "__main__":
    unittest.main()
