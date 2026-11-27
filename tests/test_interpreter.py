"""Тесты декодирования, памяти УВМ и копирования массива."""

import json
import tempfile
import unittest
from pathlib import Path

from src.assembler import encode_program, load_program, parse_program
from src.interpreter import Machine, MachineError
from src.interpreter import decode_command, make_dump, save_dump

ROOT = Path(__file__).resolve().parent.parent


def example(name):
    """Ассемблировать пример из папки examples."""
    return encode_program(load_program(ROOT / "examples" / name))


class DecodeTest(unittest.TestCase):
    """Декодер восстанавливает команды из машинного кода."""

    def test_spec_decode(self):
        """Все размеры и поля соответствуют спецификации."""
        data = bytes.fromhex("6D 08 00 03 E4 1B 00 00")
        expected = [("load", 269, 3), ("read", 0, 4), ("store", 892, 8)]
        offset = 0
        for name, argument, end in expected:
            command, offset = decode_command(data, offset)
            self.assertEqual(command["op"], name)
            self.assertEqual(command["b"], argument)
            self.assertEqual(offset, end)
        self.assertEqual(offset, len(data))

    def test_bad_binary(self):
        """Неизвестная и обрезанная команды вызывают ошибку."""
        with self.assertRaisesRegex(MachineError, "неизвестный"):
            decode_command(bytes([0]), 0)
        with self.assertRaisesRegex(MachineError, "обрезанная"):
            decode_command(bytes.fromhex("6D 08"), 0)


class MachineTest(unittest.TestCase):
    """Базовые команды и отдельная память данных."""

    def test_load_and_store(self):
        """Константа проходит через аккумулятор в память."""
        source = [{"op": "load", "arg": 42}, {"op": "store", "arg": 20}]
        machine = Machine(encode_program(parse_program(source)))
        machine.run()
        self.assertEqual(machine.accumulator, 42)
        self.assertEqual(machine.memory[20], 42)

    def test_read(self):
        """Адрес для чтения берется из аккумулятора."""
        source = [
            {"op": "load", "arg": 42},
            {"op": "store", "arg": 20},
            {"op": "load", "arg": 20},
            {"op": "read"},
        ]
        machine = Machine(encode_program(parse_program(source)))
        machine.run()
        self.assertEqual(machine.accumulator, 42)

    def test_copy_example(self):
        """Массив копируется на новые адреса без изменения источника."""
        machine = Machine(example("copy.json"))
        machine.run()
        self.assertEqual([machine.memory[a] for a in range(20, 23)],
                         [11, 22, 33])
        self.assertEqual([machine.memory[a] for a in range(30, 33)],
                         [11, 22, 33])

    def test_uninitialized_read(self):
        """Чтение неизвестного адреса не подставляет мусор."""
        program = parse_program([{"op": "read"}])
        machine = Machine(encode_program(program))
        with self.assertRaisesRegex(MachineError, "не инициализирована"):
            machine.run()

    def test_program_and_data_are_separate(self):
        """Запись данных не меняет байты памяти команд."""
        source = parse_program([{"op": "load", "arg": 9}])
        data = encode_program(source)
        machine = Machine(data)
        machine.memory[0] = 100
        self.assertEqual(machine.program, data)
        self.assertIsNot(machine.program, machine.memory)


class DumpTest(unittest.TestCase):
    """Диапазон дампа и JSON-файл."""

    def test_range_includes_empty_cells(self):
        """Диапазон включает концы и нулевые незанятые ячейки."""
        self.assertEqual(make_dump({20: 7, 22: -3}, 20, 22),
                         {"20": 7, "21": 0, "22": -3})
        with self.assertRaisesRegex(MachineError, "диапазон"):
            make_dump({}, 2, 1)
        with self.assertRaisesRegex(MachineError, "диапазон"):
            make_dump({}, -1, 1)

    def test_json_file(self):
        """Дамп сохраняется как JSON-объект с адресами и значениями."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dump.json"
            save_dump(path, {"20": 11, "21": 22})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")),
                             {"20": 11, "21": 22})


if __name__ == "__main__":
    unittest.main()
