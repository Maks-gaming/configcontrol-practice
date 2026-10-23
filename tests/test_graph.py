"""Тесты построения графа и тестового репозитория (этап 3)."""

import os
import unittest

from src.graph import all_nodes, build_graph, walk
from src.repo import RepoError, TestRepo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPHS = os.path.join(ROOT, "graphs")


def load(name, depth):
    """Построить граф A из файла graphs/<name>.txt."""
    repo = TestRepo(os.path.join(GRAPHS, name + ".txt"))
    return build_graph(repo.get_deps, "A", depth)


class BuildGraphTest(unittest.TestCase):
    """DFS на явном стеке, глубина и циклы."""

    def test_simple(self):
        """Простое дерево строится целиком."""
        graph = load("simple", 5)
        self.assertEqual(graph, {"A": ["B", "C"], "B": ["D"], "D": [],
                                 "C": ["E"], "E": []})
        self.assertEqual(walk(graph, "A")[1], [])

    def test_depth_limit(self):
        """Пакеты на предельной глубине не раскрываются."""
        graph = load("simple", 1)
        self.assertEqual(graph, {"A": ["B", "C"]})
        self.assertEqual(all_nodes(graph), ["A", "B", "C"])

    def test_cycle(self):
        """Цикл не зацикливает обход и находится как обратное ребро."""
        graph = load("cycle", 10)
        self.assertEqual(sorted(graph), ["A", "B", "C", "D", "E"])
        self.assertEqual(walk(graph, "A")[1], [("C", "A"), ("D", "D")])

    def test_diamond(self):
        """Общая зависимость D запрашивается один раз."""
        calls = []
        repo = TestRepo(os.path.join(GRAPHS, "diamond.txt"))

        def get_deps(name):
            calls.append(name)
            return repo.get_deps(name)

        build_graph(get_deps, "A", 5)
        self.assertEqual(calls.count("D"), 1)

    def test_deep_shorter_path(self):
        """J раскрывается по короткому пути, хотя есть длинный."""
        graph = load("deep", 3)
        self.assertIn("J", graph)
        self.assertNotIn("D", graph)
        self.assertEqual(len(load("deep", 20)), 11)

    def test_no_recursion_limit(self):
        """Длинная цепочка глубже лимита рекурсии Python."""
        size = 5000
        chain = {f"N{i}": [f"N{i + 1}"] for i in range(size)}
        graph = build_graph(lambda n: chain.get(n, []), "N0", size + 1)
        self.assertEqual(len(graph), size + 1)
        self.assertEqual(len(walk(graph, "N0")[0]), size + 1)


class TestRepoTest(unittest.TestCase):
    """Ошибки файла тестового репозитория."""

    def test_errors(self):
        """Неверная строка, имя, неизвестный пакет, нет файла."""
        cases = {
            "bad_line.txt": "нет двоеточия",
            "bad_name.txt": "недопустимое имя",
            "missing.txt": "не удалось прочитать",
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(RepoError) as ctx:
                    TestRepo(os.path.join(GRAPHS, name))
                self.assertIn(text, str(ctx.exception))
        repo = TestRepo(os.path.join(GRAPHS, "simple.txt"))
        with self.assertRaises(RepoError):
            repo.get_deps("Z")


if __name__ == "__main__":
    unittest.main()
