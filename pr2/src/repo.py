"""Получение прямых зависимостей пакетов из репозитория.

crates.io требует User-Agent с контактом, иначе отвечает 403.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from src.config import TEST_NAME

USER_AGENT = "cargo-graph/1.0 (study project; klimenko.m.s@edu.mirea.ru)"
TIMEOUT = 20
HTTP_NOT_FOUND = 404


class RepoError(Exception):
    """Ошибка получения данных из репозитория."""


class CratesRepo:
    """Репозиторий crates.io через его JSON API."""

    def __init__(self, base_url):
        """Запомнить адрес API, например https://crates.io/api/v1."""
        self.base_url = base_url.rstrip("/")
        self.versions = {}

    def get_json(self, path):
        """Выполнить GET-запрос к API и вернуть разобранный JSON."""
        url = self.base_url + path
        request = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code == HTTP_NOT_FOUND:
                raise RepoError(f"не найдено: {url}") from None
            raise RepoError(f"HTTP {err.code}: {url}") from None
        except urllib.error.URLError as err:
            raise RepoError(f"нет связи с {url}: {err.reason}") from None
        except ValueError:
            raise RepoError(f"ответ не JSON: {url}") from None

    def latest_version(self, name):
        """Вернуть последнюю стабильную версию крейта."""
        quoted = urllib.parse.quote(name)
        crate = self.get_json(f"/crates/{quoted}").get("crate", {})
        version = crate.get("max_stable_version") or \
            crate.get("newest_version")
        if not version:
            raise RepoError(f"у крейта {name} нет версий")
        self.versions[name] = version
        return version

    def dependencies(self, name):
        """Вернуть список (имя, требование к версии) прямых зависимостей.

        Берутся только kind=normal и не optional: dev- и
        build-зависимости и необязательные фичи не учитываются.
        """
        version = self.latest_version(name)
        quoted = urllib.parse.quote(name)
        data = self.get_json(f"/crates/{quoted}/{version}/dependencies")
        result = []
        for dep in data.get("dependencies", []):
            if dep.get("kind") != "normal" or dep.get("optional"):
                continue
            result.append((dep["crate_id"], dep.get("req", "*")))
        return result

    def get_deps(self, name):
        """Вернуть имена прямых зависимостей без повторов."""
        names = []
        for dep, _ in self.dependencies(name):
            if dep not in names:
                names.append(dep)
        return names


class TestRepo:
    """Тестовый репозиторий: граф из текстового файла.

    Каждая строка имеет вид 'A: B C' - пакет A зависит от B и C.
    Пакеты называются большими латинскими буквами, строки
    с '#' в начале и пустые строки пропускаются.
    """

    def __init__(self, path):
        """Прочитать и проверить файл графа."""
        self.graph = {}
        self.versions = {}
        try:
            with open(path, encoding="utf-8") as file:
                lines = file.read().splitlines()
        except OSError as err:
            raise RepoError(f"не удалось прочитать {path}: {err}") from None
        for number, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                self.add_line(line, f"{path}:{number}")

    def add_line(self, line, where):
        """Разобрать одну строку файла графа."""
        if ":" not in line:
            raise RepoError(f"{where}: нет двоеточия в строке '{line}'")
        name, deps = line.split(":", 1)
        names = [name.strip()] + deps.split()
        for item in names:
            if not TEST_NAME.fullmatch(item):
                raise RepoError(f"{where}: недопустимое имя '{item}'")
        if names[0] in self.graph:
            raise RepoError(f"{where}: пакет {names[0]} описан дважды")
        self.graph[names[0]] = names[1:]

    def get_deps(self, name):
        """Вернуть зависимости пакета; без строки в файле - пусто."""
        known = set(self.graph)
        for deps in self.graph.values():
            known.update(deps)
        if name not in known:
            raise RepoError(f"пакет {name} не найден в тестовом графе")
        return self.graph.get(name, [])

    def dependencies(self, name):
        """Зависимости с требованием к версии; в тесте версий нет."""
        self.versions[name] = "test"
        return [(dep, "*") for dep in self.get_deps(name)]
