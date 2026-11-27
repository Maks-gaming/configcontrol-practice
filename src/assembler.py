"""Разбор JSON-программы и перевод в промежуточное представление."""

import argparse
import json
import sys

COMMANDS = {
    "load": {"a": 5, "bits": 17},
    "read": {"a": 3, "bits": 0},
    "store": {"a": 4, "bits": 23},
    "neg": {"a": 7, "bits": 0},
}


class AssemblyError(Exception):
    """Ошибка в исходной программе."""


def parse_command(item, number):
    """Проверить одну JSON-команду и получить поля A и B."""
    if not isinstance(item, dict):
        raise AssemblyError(f"команда {number}: ожидается объект")
    name = item.get("op")
    if name not in COMMANDS:
        raise AssemblyError(f"команда {number}: неизвестная операция {name}")
    spec = COMMANDS[name]
    has_argument = spec["bits"] > 0
    expected_keys = {"op", "arg"} if has_argument else {"op"}
    if set(item) != expected_keys:
        raise AssemblyError(f"команда {number}: неверный набор полей")
    argument = item.get("arg", 0)
    if type(argument) is not int:
        raise AssemblyError(f"команда {number}: аргумент должен быть числом")
    maximum = (1 << spec["bits"]) - 1
    if argument < 0 or argument > maximum:
        raise AssemblyError(
            f"команда {number}: аргумент вне диапазона 0..{maximum}"
        )
    return {"op": name, "a": spec["a"], "b": argument}


def parse_program(data):
    """Проверить список команд и построить внутреннее представление."""
    if not isinstance(data, list):
        raise AssemblyError("корень JSON должен быть списком команд")
    return [parse_command(item, number)
            for number, item in enumerate(data, 1)]


def load_program(path):
    """Прочитать и разобрать JSON-файл с программой."""
    try:
        with open(path, encoding="utf-8") as source:
            data = json.load(source)
    except OSError as error:
        raise AssemblyError(f"не удалось прочитать файл: {error}") from error
    except json.JSONDecodeError as error:
        raise AssemblyError(f"ошибка JSON: {error}") from error
    return parse_program(data)


def format_ir(program):
    """Оформить промежуточное представление для тестового вывода."""
    lines = []
    for number, command in enumerate(program, 1):
        fields = f"A={command['a']}"
        if COMMANDS[command["op"]]["bits"] > 0:
            fields += f", B={command['b']}"
        lines.append(f"{number}. {command['op']}: {fields}")
    return "\n".join(lines)


def parse_args(argv=None):
    """Разобрать аргументы командной строки ассемблера."""
    parser = argparse.ArgumentParser(description="Ассемблер УВМ, вариант 16")
    parser.add_argument("source", help="путь к JSON-файлу программы")
    parser.add_argument("output", help="путь к двоичному результату")
    parser.add_argument("--test", action="store_true",
                        help="вывести промежуточное представление")
    return parser.parse_args(argv)


def main(argv=None):
    """Выполнить разбор программы и показать тестовое представление."""
    args = parse_args(argv)
    try:
        program = load_program(args.source)
    except AssemblyError as error:
        print(f"Ошибка ассемблера: {error}", file=sys.stderr)
        return 1
    if args.test:
        print(format_ir(program))
    print(f"Разобрано команд: {len(program)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
