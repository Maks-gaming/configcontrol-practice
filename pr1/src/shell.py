"""Логика оболочки без GUI: выполнение команд."""

import getpass
import socket

from src.parser import ParseError, parse_line
from src.vfs import VfsError, empty_vfs, load_vfs, vfs_stats

LS_OPTIONS = "la"
CD_MAX_ARGS = 1


class ShellError(Exception):
    """Ошибка выполнения команды (выводится пользователю)."""


def get_user_host():
    """Вернуть строку username@hostname реальной ОС."""
    return f"{getpass.getuser()}@{socket.gethostname()}"


class Shell:
    """Оболочка: хранит состояние и выполняет команды."""

    def __init__(self):
        """Создать оболочку с таблицей команд."""
        self.running = True
        self.vfs = empty_vfs()
        self.vfs_source = "default (empty)"
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
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
            except VfsError as error:
                output(f"error: VFS: {error}", False)
        if script_path:
            self.run_script(script_path, output)

    def prompt(self):
        """Вернуть приглашение командной строки."""
        return f"{get_user_host()}:~$ "

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

    def cmd_ls(self, args):
        """Заглушка ls: проверить опции и вывести имя и аргументы."""
        for arg in args:
            if arg.startswith("-"):
                check_options("ls", arg, LS_OPTIONS)
        return format_stub("ls", args)

    def cmd_cd(self, args):
        """Заглушка cd: принимает не больше одного аргумента."""
        if len(args) > CD_MAX_ARGS:
            raise ShellError("cd: too many arguments")
        return format_stub("cd", args)

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


def format_stub(name, args):
    """Сформировать вывод заглушки: имя команды и ее аргументы."""
    return f"{name}: args={args}"
