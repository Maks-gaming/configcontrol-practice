"""Точка входа: разбор параметров и запуск эмулятора."""

from src.config import config_lines, parse_args
from src.gui import EmulatorWindow


def main(argv=None):
    """Вывести параметры запуска в консоль и открыть окно эмулятора."""
    config = parse_args(argv)
    for line in config_lines(config):
        print(line)
    EmulatorWindow(config).run()


if __name__ == "__main__":
    main()
