"""Логика оболочки без GUI: выполнение команд."""

import fnmatch
import getpass
import socket

from src.parser import ParseError, parse_line
from src.vfs import (VfsError, empty_vfs, get_node, join_path, load_vfs,
                     split_path, vfs_stats)

LS_OPTIONS = "la"
RM_OPTIONS = "r"
CD_MAX_ARGS = 1
DIR_MODE = "drwxr-xr-x"
FILE_MODE = "-rw-r--r--"
SIZE_WIDTH = 6


class ShellError(Exception):
    """Ошибка выполнения команды (выводится пользователю)."""


def get_user_host():
    """Вернуть строку username@hostname реальной ОС."""
    return f"{getpass.getuser()}@{socket.gethostname()}"


def default_home():
    """Домашний каталог в VFS: /home/имя_пользователя_ОС."""
    return "/home/" + getpass.getuser()


class Shell:
    """Оболочка: хранит состояние и выполняет команды."""

    def __init__(self, home=None):
        """Создать оболочку, home - домашний каталог в VFS."""
        self.running = True
        self.user_home = split_path([], home or default_home(), [])
        self.home = []
        self.cwd = []
        self.vfs = empty_vfs()
        self.vfs_source = "default (empty)"
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "whoami": self.cmd_whoami,
            "find": self.cmd_find,
            "rm": self.cmd_rm,
            "exit": self.cmd_exit,
            "vfs-info": self.cmd_vfs_info,
        }

    def start(self, vfs_path, script_path, output):
        """Загрузить VFS и выполнить стартовый скрипт, если они заданы.

        Если VFS не загрузилась, остается пустая VFS по умолчанию.
        """
        if vfs_path:
            try:
                self.vfs = load_vfs(vfs_path)
                self.vfs_source = vfs_path
                output(f"VFS loaded: {vfs_path}", True)
                self.go_home()
            except VfsError as error:
                output(f"error: VFS: {error}", False)
        if script_path:
            self.run_script(script_path, output)

    def go_home(self):
        """Выбрать домашний каталог в VFS и перейти в него.

        Порядок: /home/<пользователь ОС>, первый каталог в /home,
        иначе корень /. Так эмулятор не зависит от имени в ОС.
        """
        self.home = []
        node = get_node(self.vfs, self.user_home)
        homes = get_node(self.vfs, ["home"])
        if node is not None and node.is_dir:
            self.home = list(self.user_home)
        elif homes is not None and homes.is_dir:
            dirs = [name for name in sorted(homes.children)
                    if homes.children[name].is_dir]
            self.home = ["home", dirs[0]] if dirs else []
        self.cwd = list(self.home)

    def prompt(self):
        """Вернуть приглашение: user@host и текущий каталог."""
        path = join_path(self.cwd)
        home = join_path(self.home)
        if self.home and self.cwd[:len(self.home)] == self.home:
            path = "~" + path[len(home):]
        return f"{get_user_host()}:{path}$ "

    def execute(self, line):
        """Выполнить строку и вернуть текст вывода.

        При ошибке выбрасывает ShellError.
        """
        try:
            words = parse_line(line)
        except ParseError as error:
            raise ShellError(str(error)) from error
        if not words:
            return ""
        name, args = words[0], words[1:]
        if name not in self.commands:
            raise ShellError(f"{name}: command not found")
        return self.commands[name](args)

    def run_line(self, line):
        """Выполнить строку и вернуть (вывод, успех) без исключений."""
        try:
            return self.execute(line), True
        except ShellError as error:
            return f"error: {error}", False

    def run_script(self, path, output):
        """Выполнить стартовый скрипт построчно.

        output(text, ok) вызывается для каждой строки вывода. Пустые
        строки и комментарии (#) пропускаются, строки с ошибкой
        сообщаются и тоже пропускаются. Возвращает число ошибок.
        """
        try:
            with open(path, encoding="utf-8") as file:
                lines = file.read().splitlines()
        except OSError as error:
            output(f"error: cannot read script {path}: {error}", False)
            return 1
        errors = 0
        for number, line in enumerate(lines, start=1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            output(self.prompt() + line, True)
            text, ok = self.run_line(line)
            if not ok:
                errors += 1
                text = f"{path}:{number}: {text}"
            if text:
                output(text, ok)
            if not self.running:
                break
        return errors

    def resolve(self, path):
        """Вернуть путь списком имен и узел VFS (или None)."""
        parts = split_path(self.cwd, path, self.home)
        return parts, get_node(self.vfs, parts)

    def cmd_ls(self, args):
        """Показать содержимое каталогов или имена файлов.

        Опции: -l подробный вывод, -a показать скрытые файлы.
        """
        options, paths = split_options("ls", args, LS_OPTIONS)
        paths = paths or ["."]
        blocks = []
        for path in paths:
            _, node = self.resolve(path)
            if node is None:
                raise ShellError(f"ls: cannot access '{path}': "
                                 "No such file or directory")
            lines = list_node(node, path, options)
            if len(paths) > 1 and node.is_dir:
                lines.insert(0, f"{path}:")
            blocks.append("\n".join(lines))
        separator = "\n\n" if len(paths) > 1 else "\n"
        return separator.join(block for block in blocks if block)

    def cmd_cd(self, args):
        """Сменить текущий каталог, без аргумента перейти в домашний."""
        if len(args) > CD_MAX_ARGS:
            raise ShellError("cd: too many arguments")
        path = args[0] if args else "~"
        parts, node = self.resolve(path)
        if node is None:
            raise ShellError(f"cd: {path}: No such file or directory")
        if not node.is_dir:
            raise ShellError(f"cd: {path}: Not a directory")
        self.cwd = parts
        return ""

    def cmd_whoami(self, args):
        """Вывести имя пользователя реальной ОС."""
        if args:
            raise ShellError(f"whoami: extra operand '{args[0]}'")
        return getpass.getuser()

    def cmd_find(self, args):
        """Найти файлы и каталоги: find [путь] [-name шаблон]."""
        path = "."
        if args and not args[0].startswith("-"):
            path, args = args[0], args[1:]
        pattern = parse_find_args(args)
        parts, node = self.resolve(path)
        if node is None:
            raise ShellError(f"find: '{path}': No such file or directory")
        if path == "~" or path.startswith("~/"):
            path = join_path(self.home) + path[1:]
        found = walk(node, path, parts[-1] if parts else "/")
        return "\n".join(
            text for text, name in found
            if pattern is None or fnmatch.fnmatchcase(name, pattern)
        )

    def cmd_rm(self, args):
        """Удалить файлы, с -r также каталоги.

        Удаление идет только в памяти, XML-файл VFS не меняется.
        """
        options, paths = split_options("rm", args, RM_OPTIONS)
        if not paths:
            raise ShellError("rm: missing operand")
        for path in paths:
            self.remove(path, "r" in options)
        return ""

    def remove(self, path, recursive):
        """Удалить один узел VFS по пути с проверками как в UNIX."""
        parts, node = self.resolve(path)
        if path.rstrip("/").split("/")[-1] in (".", ".."):
            raise ShellError("rm: refusing to remove '.' or '..' "
                             f"directory: skipping '{path}'")
        if node is None or not path:
            raise ShellError(f"rm: cannot remove '{path}': "
                             "No such file or directory")
        if node.is_dir and not recursive:
            raise ShellError(f"rm: cannot remove '{path}': Is a directory")
        if not parts:
            raise ShellError("rm: it is dangerous to operate "
                             "recursively on '/'")
        parent = get_node(self.vfs, parts[:-1])
        del parent.children[parts[-1]]
        if self.cwd[:len(parts)] == parts:
            self.cwd = parts[:-1]

    def cmd_exit(self, args):
        """Завершить работу оболочки, аргументы не принимаются."""
        if args:
            raise ShellError("exit: too many arguments")
        self.running = False
        return ""

    def cmd_vfs_info(self, args):
        """Служебная команда: источник и размеры загруженной VFS."""
        if args:
            raise ShellError("vfs-info: too many arguments")
        stats = vfs_stats(self.vfs)
        return "\n".join([
            f"source: {self.vfs_source}",
            f"dirs: {stats['dirs']}, files: {stats['files']}",
            f"size: {stats['bytes']} bytes, depth: {stats['depth']}",
        ])


def check_options(command, arg, allowed):
    """Проверить, что все буквы опции arg есть в allowed."""
    for letter in arg[1:]:
        if letter not in allowed:
            raise ShellError(f"{command}: invalid option -- '{letter}'")


def split_options(command, args, allowed):
    """Разделить аргументы на набор букв опций и остальные слова."""
    options = set()
    words = []
    for arg in args:
        if arg.startswith("-") and arg != "-":
            check_options(command, arg, allowed)
            options.update(arg[1:])
        else:
            words.append(arg)
    return options, words


def format_entry(name, node, long_format):
    """Строка вывода ls для одного узла."""
    if not long_format:
        return name
    mode = DIR_MODE if node.is_dir else FILE_MODE
    size = 0 if node.is_dir else len(node.data)
    return f"{mode} {size:>{SIZE_WIDTH}} {name}"


def list_node(node, path, options):
    """Строки вывода ls для файла или каталога."""
    long_format = "l" in options
    if not node.is_dir:
        return [format_entry(path, node, long_format)]
    entries = []
    if "a" in options:
        entries = [(".", node), ("..", node)]
    for name in sorted(node.children):
        if "a" in options or not name.startswith("."):
            entries.append((name, node.children[name]))
    return [format_entry(name, child, long_format)
            for name, child in entries]


def parse_find_args(args):
    """Разобрать выражение find, вернуть шаблон -name или None."""
    pattern = None
    while args:
        if args[0] != "-name":
            raise ShellError(f"find: unknown predicate '{args[0]}'")
        if len(args) == 1:
            raise ShellError("find: missing argument to '-name'")
        pattern, args = args[1], args[2:]
    return pattern


def walk(node, text, name):
    """Обойти дерево, вернуть пары (путь для вывода, имя узла)."""
    found = [(text, name)]
    prefix = text if text.endswith("/") else text + "/"
    for child_name in sorted(node.children):
        child = node.children[child_name]
        found.extend(walk(child, prefix + child_name, child_name))
    return found
