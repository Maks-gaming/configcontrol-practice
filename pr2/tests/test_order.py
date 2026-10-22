"""Тесты порядка загрузки зависимостей (этап 4)."""

import os
import unittest

from src.graph import build_graph, load_order
from src.repo import TestRepo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def order_of(name, depth=10):
    """Граф A из graphs/<name>.txt и его порядок загрузки."""
    repo = TestRepo(os.path.join(ROOT, "graphs", name + ".txt"))
    graph = build_graph(repo.get_deps, "A", depth)
    return graph, load_order(graph, "A")


class LoadOrderTest(unittest.TestCase):
    """Зависимости всегда раньше зависящих пакетов."""

    def assert_topological(self, graph, order, cycles):
        """Каждое ребро, кроме ребер цикла, идет назад по порядку."""
        place = {name: i for i, name in enumerate(order)}
        for name, deps in graph.items():
            for dep in deps:
                if (name, dep) not in cycles:
                    self.assertLess(place[dep], place[name])

    def test_simple(self):
        """Простое дерево."""
        graph, (order, cycles) = order_of("simple")
        self.assertEqual(order, ["D", "B", "E", "C", "A"])
        self.assert_topological(graph, order, cycles)

    def test_diamond(self):
        """Общая зависимость загружается один раз и раньше B и C."""
        graph, (order, cycles) = order_of("diamond")
        self.assertEqual(order, ["E", "D", "B", "C", "A"])
        self.assertEqual(cycles, [])

    def test_cycle(self):
        """В цикле порядок есть, ребро цикла сообщается."""
        graph, (order, cycles) = order_of("cycle")
        self.assertEqual(sorted(order), ["A", "B", "C", "D", "E"])
        self.assertEqual(cycles, [("C", "A"), ("D", "D")])
        self.assert_topological(graph, order, cycles)

    def test_deep_with_limit(self):
        """С пределом глубины в порядке только достигнутые пакеты."""
        graph, (order, cycles) = order_of("deep", 3)
        self.assertEqual(order, ["D", "C", "B", "K", "J", "A"])
        self.assert_topological(graph, order, cycles)


if __name__ == "__main__":
    unittest.main()
