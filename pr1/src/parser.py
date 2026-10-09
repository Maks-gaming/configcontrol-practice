"""Разбор строки команды: переменные окружения и кавычки."""

import os
import re
import shlex

VAR_PATTERN = re.compile(r"\$\{(\w+)\}|\$(\w+)")


class ParseError(Exception):
    """Ошибка разбора строки команды."""


def expand_vars(line):
    """Заменить $NAME и ${NAME} значениями из окружения ОС.

    Как в bash, неизвестная переменная заменяется пустой строкой.
    """
    def replace(match):
        """Вернуть значение переменной для найденного совпадения."""
        name = match.group(1) or match.group(2)
        return os.environ.get(name, "")

    return VAR_PATTERN.sub(replace, line)


def parse_line(line):
    """Разбить строку на имя команды и аргументы.

    Сначала раскрываются переменные, потом строка делится на слова
    с учетом кавычек. Возвращает список слов (может быть пустым).
    """
    try:
        return shlex.split(expand_vars(line))
    except ValueError as error:
        raise ParseError(f"syntax error: {error}") from error
