"""Точка входа транслятора конфигурационного языка."""

import sys

from config_language import LanguageError, translate


def main():
    """Читает учебный язык из stdin и записывает XML в stdout."""
    try:
        result = translate(sys.stdin.read())
    except LanguageError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
