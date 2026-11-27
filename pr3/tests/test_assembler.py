"""Тесты разбора JSON-программы и промежуточного представления."""

import tempfile
import unittest
from pathlib import Path

from src.assembler import AssemblyError
from src.assembler import encode_program, format_bytes, format_ir
from src.assembler import parse_program, write_binary


class AssemblerTest(unittest.TestCase):
    """Проверка команд из спецификации и ошибочных данных."""

    def test_spec_fields(self):
        """Поля A и B совпадают с тестами спецификации."""
        data = [
            {"op": "load", "arg": 269},
            {"op": "read"},
            {"op": "store", "arg": 892},
            {"op": "neg"},
        ]
        program = parse_program(data)
        self.assertEqual([item["a"] for item in program], [5, 3, 4, 7])
        self.assertEqual([item["b"] for item in program], [269, 0, 892, 0])

    def test_ir_output(self):
        """Тестовый вывод содержит имена команд и значения полей."""
        program = parse_program([{"op": "load", "arg": 269}])
        self.assertEqual(format_ir(program), "1. load: A=5, B=269")
        program = parse_program([{"op": "read"}])
        self.assertEqual(format_ir(program), "1. read: A=3")

    def test_spec_bytes(self):
        """Машинный код совпадает со всеми тестами спецификации."""
        data = [
            {"op": "load", "arg": 269},
            {"op": "read"},
            {"op": "store", "arg": 892},
            {"op": "neg"},
        ]
        program = parse_program(data)
        expected = bytes.fromhex("6D 08 00 03 E4 1B 00 00 07")
        self.assertEqual(encode_program(program), expected)
        lines = format_bytes(program, expected).splitlines()
        self.assertEqual(lines[0], "0x6D, 0x08, 0x00")
        self.assertEqual(lines[1], "0x03")
        self.assertEqual(lines[2], "0xE4, 0x1B, 0x00, 0x00")
        self.assertEqual(lines[3], "0x07")

    def test_binary_file(self):
        """Результат записывается в файл без текстового преобразования."""
        program = parse_program([{"op": "load", "arg": 269}])
        data = encode_program(program)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nested" / "program.bin"
            write_binary(path, data)
            self.assertEqual(path.read_bytes(), bytes.fromhex("6D 08 00"))

    def test_unknown_command(self):
        """Неизвестная операция отклоняется."""
        with self.assertRaisesRegex(AssemblyError, "неизвестная операция"):
            parse_program([{"op": "jump"}])

    def test_missing_argument(self):
        """Для load и store обязателен аргумент."""
        with self.assertRaisesRegex(AssemblyError, "набор полей"):
            parse_program([{"op": "load"}])

    def test_extra_argument(self):
        """У read и neg аргумента нет."""
        with self.assertRaisesRegex(AssemblyError, "набор полей"):
            parse_program([{"op": "neg", "arg": 1}])

    def test_argument_type(self):
        """Строки и логические значения не принимаются как аргумент."""
        for value in ["12", True, 1.5]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(AssemblyError, "числом"):
                    parse_program([{"op": "load", "arg": value}])

    def test_argument_range(self):
        """Аргумент не должен выходить за отведенные биты."""
        with self.assertRaisesRegex(AssemblyError, "диапазона"):
            parse_program([{"op": "load", "arg": 131072}])
        with self.assertRaisesRegex(AssemblyError, "диапазона"):
            parse_program([{"op": "store", "arg": -1}])

    def test_root_and_item_types(self):
        """Программа является списком JSON-объектов."""
        with self.assertRaisesRegex(AssemblyError, "списком"):
            parse_program({"op": "read"})
        with self.assertRaisesRegex(AssemblyError, "объект"):
            parse_program(["read"])


if __name__ == "__main__":
    unittest.main()
