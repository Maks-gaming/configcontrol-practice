"""Графический интерфейс эмулятора на tkinter."""

import tkinter as tk

from src.shell import Shell, get_user_host

FONT = ("Monospace", 11)
BG_COLOR = "black"
FG_COLOR = "lightgray"
ERROR_COLOR = "tomato"


class EmulatorWindow:
    """Окно эмулятора: поле вывода и строка ввода."""

    def __init__(self, shell=None):
        """Создать окно и виджеты."""
        self.shell = shell or Shell()
        self.root = tk.Tk()
        self.root.title(f"Эмулятор - [{get_user_host()}]")
        self.output = tk.Text(
            self.root, font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            state=tk.DISABLED, wrap=tk.WORD,
        )
        self.output.tag_configure("error", foreground=ERROR_COLOR)
        self.output.pack(fill=tk.BOTH, expand=True)
        self.entry = tk.Entry(
            self.root, font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            insertbackground=FG_COLOR,
        )
        self.entry.pack(fill=tk.X)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()

    def write(self, text, tag=None):
        """Добавить строку текста в поле вывода."""
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", tag)
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)

    def run_command(self, line):
        """Показать команду с приглашением, выполнить и вывести результат."""
        self.write(self.shell.prompt() + line)
        text, ok = self.shell.run_line(line)
        if text:
            self.write(text, None if ok else "error")
        if not self.shell.running:
            self.root.destroy()

    def on_enter(self, _event):
        """Обработать нажатие Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.run_command(line)

    def run(self):
        """Запустить главный цикл окна."""
        self.root.mainloop()
