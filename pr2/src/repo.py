"""Получение прямых зависимостей пакетов из репозитория."""

import json
import urllib.error
import urllib.parse
import urllib.request

# crates.io требует User-Agent с контактом, иначе отвечает 403.
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
