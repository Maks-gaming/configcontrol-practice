"""Загрузка и проверка конфигурации из XML-файла.

KEYS задает порядок параметров, в нем же они печатаются.
CRATE_NAME - имя крейта на crates.io: латиница, цифры, '-' и '_',
до 64 символов. TEST_NAME - имя пакета в тестовом репозитории:
большие латинские буквы.
"""

import os
import re
import xml.etree.ElementTree as etree

KEYS = ("package", "repository", "test_mode", "ascii_tree", "max_depth")
TRUE_WORDS = ("true", "yes", "1")
FALSE_WORDS = ("false", "no", "0")
MIN_DEPTH = 1
CRATE_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")
TEST_NAME = re.compile(r"[A-Z]+")


class ConfigError(Exception):
    """Ошибка в конфигурационном файле."""


def read_xml(path):
    """Прочитать XML-файл и вернуть словарь текстов элементов."""
    if not os.path.isfile(path):
        raise ConfigError(f"файл конфигурации не найден: {path}")
    try:
        root = etree.parse(path).getroot()
    except etree.ParseError as err:
        raise ConfigError(f"неверный формат XML: {err}") from err
    if root.tag != "config":
        raise ConfigError(f"корневой элемент должен быть <config>, "
                          f"а не <{root.tag}>")
    raw = {}
    for item in root:
        if item.tag not in KEYS:
            raise ConfigError(f"неизвестный параметр: <{item.tag}>")
        if item.tag in raw:
            raise ConfigError(f"параметр <{item.tag}> задан дважды")
        raw[item.tag] = (item.text or "").strip()
    for key in KEYS:
        if key not in raw:
            raise ConfigError(f"не задан параметр <{key}>")
    return raw


def parse_bool(key, text):
    """Перевести true/false в bool, иначе ошибка."""
    word = text.lower()
    if word in TRUE_WORDS:
        return True
    if word in FALSE_WORDS:
        return False
    raise ConfigError(f"{key}: ожидается true или false, получено "
                      f"'{text}'")


def parse_depth(text):
    """Проверить, что глубина - целое число не меньше 1."""
    try:
        depth = int(text)
    except ValueError:
        raise ConfigError(f"max_depth: ожидается целое число, получено "
                          f"'{text}'") from None
    if depth < MIN_DEPTH:
        raise ConfigError(f"max_depth: должна быть не меньше "
                          f"{MIN_DEPTH}, получено {depth}")
    return depth


def check_package(name, test_mode):
    """Проверить имя пакета с учетом режима."""
    if not name:
        raise ConfigError("package: имя пакета не может быть пустым")
    pattern = TEST_NAME if test_mode else CRATE_NAME
    if not pattern.fullmatch(name):
        hint = "большие латинские буквы" if test_mode else \
            "латиница, цифры, '-' и '_'"
        raise ConfigError(f"package: недопустимое имя '{name}' ({hint})")


def check_repository(path, test_mode):
    """Проверить URL репозитория или путь к тестовому файлу."""
    if not path:
        raise ConfigError("repository: адрес не может быть пустым")
    if test_mode:
        if not os.path.isfile(path):
            raise ConfigError(f"repository: файл тестового "
                              f"репозитория не найден: {path}")
    elif not path.startswith(("http://", "https://")):
        raise ConfigError(f"repository: ожидается URL http(s)://, "
                          f"получено '{path}'")


def load_config(path):
    """Загрузить конфигурацию, вернуть словарь проверенных значений.

    Путь к тестовому файлу считается от папки конфига.
    """
    raw = read_xml(path)
    test_mode = parse_bool("test_mode", raw["test_mode"])
    repository = raw["repository"]
    if test_mode and repository:
        folder = os.path.dirname(os.path.abspath(path))
        repository = os.path.normpath(os.path.join(folder, repository))
    check_package(raw["package"], test_mode)
    check_repository(repository, test_mode)
    return {
        "package": raw["package"],
        "repository": repository,
        "test_mode": test_mode,
        "ascii_tree": parse_bool("ascii_tree", raw["ascii_tree"]),
        "max_depth": parse_depth(raw["max_depth"]),
    }


def config_lines(config):
    """Вернуть параметры в виде строк ключ=значение."""
    lines = []
    for key in KEYS:
        value = config[key]
        if isinstance(value, bool):
            value = str(value).lower()
        lines.append(f"{key}={value}")
    return lines
