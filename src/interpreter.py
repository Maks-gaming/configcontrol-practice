"""Интерпретатор УВМ: цикл команд, память данных и JSON-дамп."""

import argparse
import json
import sys
from pathlib import Path

from src.assembler import COMMANDS

OP_NAMES = {spec["a"]: name for name, spec in COMMANDS.items()}


class MachineError(Exception):
    """Ошибка машинного кода или выполнения программы."""


def decode_command(data, offset):
    """Декодировать команду и вернуть ее вместе со следующим адресом."""
    if offset >= len(data):
        raise MachineError("неожиданный конец машинного кода")
    opcode = data[offset] & 7
    if opcode not in OP_NAMES:
        raise MachineError(f"неизвестный код операции {opcode}")
    name = OP_NAMES[opcode]
    spec = COMMANDS[name]
    end = offset + spec["size"]
    if end > len(data):
        raise MachineError("обрезанная машинная команда")
    value = int.from_bytes(data[offset:end], byteorder="little")
    command = {"op": name, "a": opcode, "b": value >> 3}
    return command, end


def load_binary(path):
    """Прочитать ассемблированную программу из двоичного файла."""
    try:
        return Path(path).read_bytes()
    except OSError as error:
        raise MachineError(f"не удалось прочитать файл: {error}") from error


class Machine:
    """УВМ с аккумулятором и отдельными памятью команд и данных."""

    def __init__(self, program):
        """Сохранить байты команд и создать пустую память данных."""
        self.program = program
        self.memory = {}
        self.accumulator = 0

    def read_memory(self):
        """Прочитать память по адресу из аккумулятора."""
        address = self.accumulator
        if address < 0 or address not in self.memory:
            message = f"память по адресу {address} не инициализирована"
            raise MachineError(message)
        self.accumulator = self.memory[address]

    def execute(self, command):
        """Выполнить одну декодированную команду."""
        name = command["op"]
        if name == "load":
            self.accumulator = command["b"]
        elif name == "read":
            self.read_memory()
        elif name == "store":
            self.memory[command["b"]] = self.accumulator
        elif name == "neg":
            self.accumulator = -self.accumulator
        else:
            raise MachineError(f"неизвестная операция {name}")

    def run(self):
        """Выполнять команды до конца памяти программы."""
        offset = 0
        while offset < len(self.program):
            command, offset = decode_command(self.program, offset)
            self.execute(command)


def make_dump(memory, start, end):
    """Получить значения всех адресов в включительном диапазоне."""
    if start < 0 or end < start:
        raise MachineError("неверный диапазон адресов дампа")
    return {str(address): memory.get(address, 0)
            for address in range(start, end + 1)}


def save_dump(path, dump):
    """Сохранить дамп памяти в JSON-файл."""
    try:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(dump, ensure_ascii=False, indent=2) + "\n"
        output.write_text(text, encoding="utf-8")
    except OSError as error:
        raise MachineError(f"не удалось записать дамп: {error}") from error


def parse_args(argv=None):
    """Разобрать аргументы командной строки интерпретатора."""
    parser = argparse.ArgumentParser(description="Интерпретатор УВМ")
    parser.add_argument("program", help="двоичный файл программы")
    parser.add_argument("dump", help="JSON-файл дампа памяти")
    parser.add_argument("start", type=int, help="первый адрес дампа")
    parser.add_argument("end", type=int, help="последний адрес дампа")
    return parser.parse_args(argv)


def main(argv=None):
    """Запустить программу и сохранить выбранный диапазон памяти."""
    args = parse_args(argv)
    try:
        machine = Machine(load_binary(args.program))
        machine.run()
        dump = make_dump(machine.memory, args.start, args.end)
        save_dump(args.dump, dump)
    except MachineError as error:
        print(f"Ошибка интерпретатора: {error}", file=sys.stderr)
        return 1
    print(json.dumps(dump, ensure_ascii=False))
    print(f"Дамп памяти: {args.dump}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
