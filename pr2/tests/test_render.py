"""Тесты визуализации и запуска CLI (этап 5)."""

import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from src.graph import build_graph
from src.main import main
from src.render import ascii_tree, render, to_dot
from src.repo import TestRepo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def graph_of(name, depth=5):
    """Граф A из graphs/<name>.txt."""
    repo = TestRepo(os.path.join(ROOT, "graphs", name + ".txt"))
    return build_graph(repo.get_deps, "A", depth)


class DotTest(unittest.TestCase):
    """Текст на языке Graphviz."""

    def test_cycle_edges_red(self):
        """Все ребра есть, ребра циклов красные."""
        text = to_dot(graph_of("cycle"), "A")
        self.assertTrue(text.startswith('digraph "A" {'))
        self.assertIn('"A" -> "B";', text)
        self.assertIn('"C" -> "A" [color=red];', text)
        self.assertIn('"D" -> "D" [color=red];', text)

    def test_depth_leaf_dashed(self):
        """Нераскрытый пакет нарисован пунктиром."""
        text = to_dot(graph_of("deep", 2), "A")
        self.assertIn('"C" [style=dashed];', text)


class AsciiTreeTest(unittest.TestCase):
    """ASCII-дерево как у cargo tree --charset ascii."""

    def test_diamond(self):
        """Повтор помечен (*)."""
        self.assertEqual(ascii_tree(graph_of("diamond"), "A"), [
            "A",
            "|-- B",
            "|   `-- D",
            "|       `-- E",
            "`-- C",
            "    `-- D (*)",
        ])

    def test_cycle(self):
        """Ребро назад помечено (цикл)."""
        lines = ascii_tree(graph_of("cycle"), "A")
        self.assertIn("|       |-- A (цикл)", lines)
        self.assertIn("    `-- D (цикл)", lines)


class RenderTest(unittest.TestCase):
    """Вызов программы dot."""

    @mock.patch("shutil.which", return_value=None)
    def test_no_dot(self, which):
        """Без Graphviz возвращается понятная ошибка."""
        self.assertIn("не найдена", render("digraph {}", "x.png"))

    def test_cli_without_dot(self):
        """CLI печатает DOT и дерево, даже если dot не найден."""
        out, err = io.StringIO(), io.StringIO()
        config = os.path.join(ROOT, "configs", "test_diamond.xml")
        with tempfile.TemporaryDirectory() as folder, \
                mock.patch("shutil.which", return_value=None), \
                contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            image = os.path.join(folder, "a.png")
            code = main([config, "--image", image])
        self.assertEqual(code, 0)
        self.assertIn('"B" -> "D";', out.getvalue())
        self.assertIn("    `-- D (*)", out.getvalue())
        self.assertIn("картинка не создана", err.getvalue())

    def test_cli_error_code(self):
        """Ошибка конфигурации дает код 1."""
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["nofile.xml"]), 1)


if __name__ == "__main__":
    unittest.main()
