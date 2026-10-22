"""Точка входа: визуализация графа зависимостей пакетов Cargo."""

import argparse
import sys

from src.config import ConfigError, config_lines, load_config


def parse_args(argv=None):
    """Разобрать аргументы командной строки."""
    parser = argparse.ArgumentParser(
        prog="run.sh",
        description="Граф зависимостей пакетов Rust (Cargo).",
    )
    parser.add_argument("config", help="путь к XML-файлу конфигурации")
    return parser.parse_args(argv)


def main(argv=None):
    """Загрузить конфигурацию и напечатать параметры."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as err:
        print(f"ошибка конфигурации: {err}", file=sys.stderr)
        return 1
    for line in config_lines(config):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
