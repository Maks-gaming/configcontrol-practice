"""Визуализация графа: Graphviz DOT, картинка и ASCII-дерево."""

import shutil
import subprocess

from src.graph import all_nodes, walk


def quote(name):
    """Взять имя в кавычки для языка DOT."""
    return '"' + name.replace('"', '\\"') + '"'


def to_dot(graph, root):
    """Вернуть текст графа на языке Graphviz DOT.

    Корень выделен цветом, ребра циклов красные, нераскрытые
    из-за предела глубины пакеты нарисованы пунктиром.
    """
    cycles = walk(graph, root)[1]
    lines = [f"digraph {quote(root)} {{",
             "    rankdir=LR;",
             '    node [shape=box, fontname="Helvetica"];',
             f"    {quote(root)} [style=filled, fillcolor=lightblue];"]
    for name in all_nodes(graph):
        if name not in graph:
            lines.append(f"    {quote(name)} [style=dashed];")
    for name, deps in graph.items():
        for dep in deps:
            attrs = " [color=red]" if (name, dep) in cycles else ""
            lines.append(f"    {quote(name)} -> {quote(dep)}{attrs};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def ascii_tree(graph, root):
    """Вернуть строки ASCII-дерева, как у cargo tree --charset ascii.

    Обход тоже без рекурсии, на стеке. Уже показанный пакет
    помечается (*) и второй раз не раскрывается, ребро назад
    по циклу помечается (цикл).
    """
    lines = [root]
    shown = {root}
    stack = children(graph, root, "", (root,))
    while stack:
        dep, prefix, path, last = stack.pop()
        mark = ""
        if dep in path:
            mark = " (цикл)"
        elif dep in shown and graph.get(dep):
            mark = " (*)"
        lines.append(prefix + ("`-- " if last else "|-- ") + dep + mark)
        if not mark:
            shown.add(dep)
            stack.extend(children(graph, dep,
                                  prefix + ("    " if last else "|   "),
                                  path + (dep,)))
    return lines


def children(graph, name, prefix, path):
    """Элементы стека для зависимостей name, первая - сверху."""
    deps = graph.get(name, [])
    items = [(dep, prefix, path, number == len(deps))
             for number, dep in enumerate(deps, 1)]
    return items[::-1]


def render(dot_text, path, fmt="png"):
    """Нарисовать картинку программой dot из Graphviz.

    Возвращает None при успехе или текст ошибки, если dot
    не установлен или завершился с ошибкой.
    """
    dot = shutil.which("dot")
    if dot is None:
        return "программа dot (Graphviz) не найдена в PATH"
    result = subprocess.run([dot, f"-T{fmt}", "-o", path],
                            input=dot_text.encode("utf-8"),
                            capture_output=True, check=False)
    if result.returncode != 0:
        return result.stderr.decode("utf-8", "replace").strip()
    return None
