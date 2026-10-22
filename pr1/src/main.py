"""Точка входа: разбор параметров и запуск эмулятора."""

import sys

from src.config import config_lines, parse_args


def main(argv=None):
    """Вывести параметры запуска в консоль и открыть окно эмулятора.

    GUI импортируется после разбора параметров, поэтому --help
    работает даже там, где нет tkinter. Вывод переводится в UTF-8,
    чтобы кириллица не ломала запуск в консоли Windows.
    """
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    config = parse_args(argv)
    for line in config_lines(config):
        print(line)
    try:
        from src.gui import EmulatorWindow
    except ImportError:
        sys.exit("ошибка: нужен tkinter (пакет python3-tk)")
    EmulatorWindow(config).run()


if __name__ == "__main__":
    main()
