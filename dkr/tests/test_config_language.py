"""Тесты парсера, вычислений, XML и командной строки."""

from pathlib import Path
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config_language import LanguageError, translate


class TranslatorTests(unittest.TestCase):
    """Проверяет конструкции языка и сообщения об ошибках."""

    def parse(self, text):
        """Транслирует текст и разбирает полученный XML."""
        return ET.fromstring(translate(text))

    def test_signed_numbers(self):
        """Разбирает положительные, отрицательные и нулевые числа."""
        root = self.parse("+12 -7 0")
        values = [element.text for element in root]
        self.assertEqual(values, ["12", "-7", "0"])
        self.assertTrue(all(item.get("type") == "number" for item in root))

    def test_string_and_xml_escaping(self):
        """Сохраняет Unicode и экранирует специальные символы XML."""
        root = self.parse('"Привет <>&"')
        self.assertEqual(root[0].get("type"), "string")
        self.assertEqual(root[0].text, "Привет <>&")

    def test_nested_arrays(self):
        """Разбирает пустые и вложенные массивы."""
        root = self.parse('[1 ["text" [2 -3]] []]')
        array = root[0]
        self.assertEqual(array.get("type"), "array")
        self.assertEqual(len(array), 3)
        self.assertEqual(array[1][1][0].text, "2")
        self.assertEqual(array[1][1][1].text, "-3")
        self.assertEqual(len(array[2]), 0)

    def test_constant_value_types(self):
        """Объявляет числовые, строковые и массивные константы."""
        root = self.parse('(def number 4)(def text "abc")(def list [1 2])')
        self.assertEqual([item.get("name") for item in root],
                         ["number", "text", "list"])
        self.assertEqual([item.get("type") for item in root],
                         ["number", "string", "array"])

    def test_all_operations(self):
        """Вычисляет сложение, вычитание, mod и abs."""
        root = self.parse(
            "(def base 10)"
            "[#(base 5 +) #(base 3 -) #(base 4 mod()) "
            "#(base 20 - abs())]"
        )
        values = [item.text for item in root[1]]
        self.assertEqual(values, ["15", "7", "2", "10"])

    def test_nested_expressions(self):
        """Вычисляет выражения внутри выражений и массивов."""
        root = self.parse("(def n 5)[#(n #(2 3 +) +) [#(n 1 -)]]")
        self.assertEqual(root[1][0].text, "10")
        self.assertEqual(root[1][1][0].text, "4")

    def test_constant_from_expression(self):
        """Использует ранее вычисленную константу в другом выражении."""
        root = self.parse("(def a 2)(def b #(a 3 +))#(b 4 +)")
        self.assertEqual(root[1].text, "5")
        self.assertEqual(root[2].text, "9")

    def test_undefined_constant(self):
        """Сообщает о необъявленной константе."""
        with self.assertRaisesRegex(LanguageError, "Неизвестная константа"):
            translate("#(missing 1 +)")

    def test_duplicate_constant(self):
        """Запрещает повторное объявление одной константы."""
        with self.assertRaisesRegex(LanguageError, "уже объявлена"):
            translate("(def value 1)(def value 2)")

    def test_missing_operand(self):
        """Обнаруживает нехватку операндов."""
        with self.assertRaisesRegex(LanguageError, "Недостаточно операндов"):
            translate("#(1 +)")

    def test_extra_expression_value(self):
        """Требует одно итоговое значение выражения."""
        with self.assertRaisesRegex(LanguageError, "одно значение"):
            translate("#(1 2)")

    def test_modulo_by_zero(self):
        """Обнаруживает деление на ноль в mod."""
        with self.assertRaisesRegex(LanguageError, "Деление на ноль"):
            translate("#(5 0 mod())")

    def test_non_number_operand(self):
        """Запрещает арифметику со строковой константой."""
        with self.assertRaisesRegex(LanguageError, "только числа"):
            translate('(def text "abc")#(text 1 +)')

    def test_invalid_name(self):
        """Запрещает цифры в имени константы."""
        with self.assertRaisesRegex(LanguageError, "Синтаксическая ошибка"):
            translate("(def abc1 2)")

    def test_unclosed_array(self):
        """Сообщает позицию незакрытого массива."""
        with self.assertRaisesRegex(LanguageError, "строке 1"):
            translate("[1 2")

    def test_unknown_token(self):
        """Отклоняет неизвестную операцию."""
        with self.assertRaisesRegex(LanguageError, "Синтаксическая ошибка"):
            translate("#(2 3 *)")

    def test_empty_input(self):
        """Создает пустой корневой элемент для пустого ввода."""
        root = self.parse("")
        self.assertEqual(root.tag, "config")
        self.assertEqual(len(root), 0)


class CommandLineTests(unittest.TestCase):
    """Проверяет стандартные потоки и коды завершения."""

    def run_cli(self, text):
        """Запускает транслятор с заданным стандартным вводом."""
        return subprocess.run(
            [sys.executable, str(ROOT / "src" / "main.py")],
            input=text,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_stdout(self):
        """Выводит только XML в stdout при успешной трансляции."""
        result = self.run_cli("(def answer 42)#(answer 1 +)")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn('<value type="number">43</value>', result.stdout)

    def test_stderr_and_exit_code(self):
        """Выводит ошибку в stderr и возвращает ненулевой код."""
        result = self.run_cli("[1")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Синтаксическая ошибка", result.stderr)

    def test_examples(self):
        """Проверяет все три примера из разных предметных областей."""
        for name in ("server", "study", "robot"):
            source = (ROOT / "examples" / f"{name}.cfg").read_text()
            expected = (ROOT / "examples" / f"{name}.xml").read_text()
            self.assertEqual(translate(source), expected)


if __name__ == "__main__":
    unittest.main()
