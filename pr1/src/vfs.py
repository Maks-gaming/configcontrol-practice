"""Виртуальная файловая система: загрузка из XML в память."""

import base64
from xml.etree import ElementTree

ROOT_TAG = "vfs"
BAD_NAMES = ("", ".", "..")


class VfsError(Exception):
    """Ошибка загрузки VFS."""


class VfsNode:
    """Узел VFS: каталог (children) или файл (data в байтах)."""

    def __init__(self, name, is_dir, data=b""):
        """Создать узел с именем name."""
        self.name = name
        self.is_dir = is_dir
        self.data = data
        self.children = {}


def empty_vfs():
    """Вернуть VFS по умолчанию: пустой корневой каталог."""
    return VfsNode("/", True)


def load_vfs(path):
    """Прочитать XML-файл и построить дерево VFS в памяти.

    Сам файл не изменяется. При ошибке выбрасывает VfsError.
    """
    try:
        tree = ElementTree.parse(path)
    except FileNotFoundError as error:
        raise VfsError(f"файл не найден: {path}") from error
    except OSError as error:
        raise VfsError(f"не удалось прочитать {path}: {error}") from error
    except ElementTree.ParseError as error:
        raise VfsError(f"неверный формат XML: {error}") from error
    element = tree.getroot()
    if element.tag != ROOT_TAG:
        raise VfsError(f"корневой элемент должен быть <{ROOT_TAG}>")
    root = empty_vfs()
    add_children(root, element)
    return root


def add_children(parent, element):
    """Добавить в каталог parent все дочерние элементы element."""
    for child in element:
        node = parse_node(child)
        if node.name in parent.children:
            raise VfsError(f"повторяющееся имя: {node.name}")
        parent.children[node.name] = node


def parse_node(element):
    """Построить узел VFS из элемента <dir> или <file>."""
    name = element.get("name", "")
    if name in BAD_NAMES or "/" in name:
        raise VfsError(f"неверное имя: '{name}'")
    if element.tag == "dir":
        node = VfsNode(name, True)
        add_children(node, element)
        return node
    if element.tag == "file":
        return VfsNode(name, False, read_data(element))
    raise VfsError(f"неизвестный элемент <{element.tag}>")


def read_data(element):
    """Вернуть содержимое файла в байтах (текст или base64)."""
    text = element.text or ""
    encoding = element.get("encoding", "text")
    if encoding == "text":
        return text.encode("utf-8")
    if encoding == "base64":
        try:
            return base64.b64decode("".join(text.split()), validate=True)
        except ValueError as error:
            name = element.get("name")
            raise VfsError(f"{name}: неверные данные base64") from error
    raise VfsError(f"неизвестная кодировка: {encoding}")


def vfs_stats(node):
    """Посчитать каталоги, файлы, байты и глубину дерева.

    Возвращает словарь, корень в число каталогов не входит.
    """
    stats = {"dirs": 0, "files": 0, "bytes": 0, "depth": 0}
    for child in node.children.values():
        if child.is_dir:
            sub = vfs_stats(child)
            stats["dirs"] += sub["dirs"] + 1
            stats["files"] += sub["files"]
            stats["bytes"] += sub["bytes"]
            stats["depth"] = max(stats["depth"], sub["depth"] + 1)
        else:
            stats["files"] += 1
            stats["bytes"] += len(child.data)
            stats["depth"] = max(stats["depth"], 1)
    return stats


def split_path(cwd, path, home):
    """Перевести путь в список имен от корня.

    cwd и home - текущий и домашний каталоги в виде списка имен.
    Поддерживаются абсолютные и относительные пути, '.', '..', '~'.
    """
    if path == "~" or path.startswith("~/"):
        parts = list(home)
        path = path[1:]
    elif path.startswith("/"):
        parts = []
    else:
        parts = list(cwd)
    for name in path.split("/"):
        if name == "..":
            if parts:
                parts.pop()
        elif name not in ("", "."):
            parts.append(name)
    return parts


def get_node(root, parts):
    """Найти узел по списку имен, вернуть None, если его нет."""
    node = root
    for name in parts:
        if not node.is_dir or name not in node.children:
            return None
        node = node.children[name]
    return node


def join_path(parts):
    """Собрать строку абсолютного пути из списка имен."""
    return "/" + "/".join(parts)
