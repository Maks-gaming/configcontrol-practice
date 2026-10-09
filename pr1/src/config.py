"""Параметры командной строки эмулятора."""

import argparse


def parse_args(argv=None):
    """Разобрать аргументы командной строки и вернуть Namespace."""
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки UNIX с GUI.",
    )
    parser.add_argument(
        "--vfs", metavar="PATH",
        help="путь к XML-файлу виртуальной файловой системы",
    )
    parser.add_argument(
        "--script", metavar="PATH",
        help="путь к стартовому скрипту с командами эмулятора",
    )
    return parser.parse_args(argv)


def config_lines(config):
    """Вернуть строки отладочного вывода всех параметров."""
    lines = ["[debug] параметры запуска:"]
    for key, value in vars(config).items():
        lines.append(f"[debug]   {key} = {value}")
    return lines
