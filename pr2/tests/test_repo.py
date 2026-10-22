"""Тесты получения зависимостей с crates.io через HTTP-моки (этап 2)."""

import io
import json
import unittest
import urllib.error
from unittest import mock

from src.repo import CratesRepo, RepoError

BASE = "https://crates.io/api/v1"
# Ответы API в сокращенном виде: url -> JSON.
RESPONSES = {
    BASE + "/crates/demo": {"crate": {"max_stable_version": "1.2.0",
                                      "newest_version": "2.0.0-beta"}},
    BASE + "/crates/demo/1.2.0/dependencies": {"dependencies": [
        {"crate_id": "itoa", "req": "^1.0", "kind": "normal",
         "optional": False},
        {"crate_id": "serde", "req": "^1", "kind": "normal",
         "optional": False},
        {"crate_id": "indexmap", "req": "^2", "kind": "normal",
         "optional": True},
        {"crate_id": "cc", "req": "^1", "kind": "build",
         "optional": False},
        {"crate_id": "trybuild", "req": "^1", "kind": "dev",
         "optional": False},
    ]},
}


def fake_urlopen(request, timeout=None):
    """Подменить сетевой запрос ответом из RESPONSES."""
    url = request.full_url
    if url not in RESPONSES:
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
    return io.BytesIO(json.dumps(RESPONSES[url]).encode())


@mock.patch("urllib.request.urlopen", side_effect=fake_urlopen)
class CratesRepoTest(unittest.TestCase):
    """Разбор ответов crates.io без обращения к сети."""

    def test_only_normal_deps(self, urlopen):
        """Берутся только обычные необязательные зависимости."""
        repo = CratesRepo(BASE + "/")
        self.assertEqual(repo.dependencies("demo"),
                         [("itoa", "^1.0"), ("serde", "^1")])
        self.assertEqual(repo.get_deps("demo"), ["itoa", "serde"])
        self.assertEqual(repo.versions["demo"], "1.2.0")

    def test_user_agent(self, urlopen):
        """В каждом запросе есть заголовок User-Agent."""
        CratesRepo(BASE).get_deps("demo")
        request = urlopen.call_args[0][0]
        self.assertIn("cargo-graph", request.get_header("User-agent"))

    def test_not_found(self, urlopen):
        """Неизвестный крейт дает RepoError."""
        with self.assertRaises(RepoError) as ctx:
            CratesRepo(BASE).get_deps("nothing")
        self.assertIn("не найдено", str(ctx.exception))

    def test_network_error(self, urlopen):
        """Нет сети - понятная ошибка."""
        urlopen.side_effect = urllib.error.URLError("timeout")
        with self.assertRaises(RepoError) as ctx:
            CratesRepo(BASE).get_deps("demo")
        self.assertIn("нет связи", str(ctx.exception))

    def test_bad_json(self, urlopen):
        """Ответ не JSON - понятная ошибка."""
        urlopen.side_effect = None
        urlopen.return_value = io.BytesIO(b"<html>")
        with self.assertRaises(RepoError):
            CratesRepo(BASE).get_deps("demo")


if __name__ == "__main__":
    unittest.main()
