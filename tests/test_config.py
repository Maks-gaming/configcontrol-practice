"""Тесты загрузки конфигурации (этап 1)."""

import os
import tempfile
import unittest

from src.config import ConfigError, config_lines, load_config

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAD = os.path.join(ROOT, "configs", "bad")
TEMPLATE = """<config>
    <package>{package}</package>
    <repository>{repository}</repository>
    <test_mode>{test_mode}</test_mode>
    <ascii_tree>{ascii_tree}</ascii_tree>
    <max_depth>{max_depth}</max_depth>
</config>
"""
GOOD = {
    "package": "serde_json",
    "repository": "https://crates.io/api/v1",
    "test_mode": "false",
    "ascii_tree": "true",
    "max_depth": "3",
}


class ConfigTest(unittest.TestCase):
    """Проверка чтения и проверки параметров."""

    def load(self, **changes):
        """Записать конфиг с изменениями во временный файл и загрузить."""
        values = dict(GOOD, **changes)
        with tempfile.NamedTemporaryFile("w", suffix=".xml",
                                         delete=False) as file:
            file.write(TEMPLATE.format(**values))
        self.addCleanup(os.remove, file.name)
        return load_config(file.name)

    def assert_error(self, text, **changes):
        """Проверить, что загрузка падает с нужным сообщением."""
        with self.assertRaises(ConfigError) as ctx:
            self.load(**changes)
        self.assertIn(text, str(ctx.exception))

    def test_good_config(self):
        """Правильный конфиг печатается как ключ=значение."""
        lines = config_lines(self.load())
        self.assertEqual(lines, [
            "package=serde_json",
            "repository=https://crates.io/api/v1",
            "test_mode=false",
            "ascii_tree=true",
            "max_depth=3",
        ])

    def test_test_mode(self):
        """В тестовом режиме repository - путь к существующему файлу."""
        path = os.path.join(ROOT, "configs", "serde_json.xml")
        config = self.load(package="A", repository=path,
                           test_mode="true")
        self.assertTrue(config["test_mode"])
        self.assert_error("не найден", package="A", test_mode="true",
                          repository="nofile.txt")
        self.assert_error("большие латинские", package="a",
                          repository=path, test_mode="true")

    def test_package_errors(self):
        """Пустое и недопустимое имя пакета."""
        self.assert_error("пустым", package="")
        self.assert_error("недопустимое", package="serde json")

    def test_repository_errors(self):
        """Пустой адрес и адрес не http(s)."""
        self.assert_error("пустым", repository="")
        self.assert_error("http(s)", repository="ftp://x")

    def test_bool_errors(self):
        """Неверные значения режимов."""
        self.assert_error("test_mode", test_mode="maybe")
        self.assert_error("ascii_tree", ascii_tree="")

    def test_depth_errors(self):
        """Глубина не число, ноль или отрицательная."""
        self.assert_error("целое число", max_depth="three")
        self.assert_error("не меньше 1", max_depth="0")
        self.assert_error("не меньше 1", max_depth="-2")

    def test_file_errors(self):
        """Ошибки самого файла: нет файла, битый XML, лишние теги."""
        cases = {
            "nofile.xml": "не найден",
            "broken_xml.xml": "неверный формат XML",
            "wrong_root.xml": "корневой элемент",
            "missing_param.xml": "не задан параметр",
            "unknown_param.xml": "неизвестный параметр",
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(ConfigError) as ctx:
                    load_config(os.path.join(BAD, name))
                self.assertIn(text, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
