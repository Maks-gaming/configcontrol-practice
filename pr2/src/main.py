"""Точка входа: визуализация графа зависимостей пакетов Cargo."""

import argparse
import os
import sys
import webbrowser
from pathlib import Path

from src.config import ConfigError, config_lines, load_config
from src.graph import all_nodes, build_graph, load_order, walk
from src.render import ascii_tree, render, to_dot
from src.repo import CratesRepo, RepoError, TestRepo

SHOW = ("params", "deps", "graph", "order", "dot")


def parse_args(argv=None):
    """Разобрать аргументы командной строки."""
    parser = argparse.ArgumentParser(
        prog="run.sh",
        description="Граф зависимостей пакетов Rust (Cargo).",
    )
    parser.add_argument("config", help="путь к XML-файлу конфигурации")
    parser.add_argument(
        "--show", choices=SHOW, default="dot",
        help="что вывести: params - параметры (этап 1), "
             "deps - прямые зависимости (этап 2), "
             "graph - граф зависимостей (этап 3), "
             "order - порядок загрузки (этап 4), "
             "dot - Graphviz и картинка (этап 5, по умолчанию)")
    parser.add_argument(
        "--image", metavar="PATH",
        help="куда сохранить картинку графа, по умолчанию "
             "out/<пакет>.png")
    parser.add_argument("--view", action="store_true",
                        help="открыть картинку после сохранения")
    return parser.parse_args(argv)


def make_repo(config):
    """Создать репозиторий по режиму из конфигурации."""
    if config["test_mode"]:
        return TestRepo(config["repository"])
    return CratesRepo(config["repository"])


def show_deps(config):
    """Напечатать прямые зависимости пакета."""
    repo = make_repo(config)
    deps = repo.dependencies(config["package"])
    version = repo.versions[config["package"]]
    print(f"{config['package']} {version}: прямых зависимостей "
          f"{len(deps)}")
    for name, req in deps:
        print(f"  {name} {req}")


def show_graph(config):
    """Построить граф и напечатать список смежности и циклы."""
    repo = make_repo(config)
    root = config["package"]
    graph = build_graph(repo.get_deps, root, config["max_depth"])
    nodes = all_nodes(graph)
    print(f"граф {root}, глубина {config['max_depth']}: "
          f"пакетов {len(nodes)}")
    for name in nodes:
        if name in graph:
            print(f"  {name} -> {' '.join(graph[name]) or '(нет)'}")
        else:
            print(f"  {name} (не раскрыт: предел глубины)")
    cycles = walk(graph, root)[1]
    for name, dep in cycles:
        print(f"цикл: {name} -> {dep}")


def show_order(config):
    """Напечатать порядок загрузки зависимостей."""
    repo = make_repo(config)
    root = config["package"]
    graph = build_graph(repo.get_deps, root, config["max_depth"])
    order, cycles = load_order(graph, root)
    print(f"порядок загрузки {root} ({len(order)} пакетов):")
    for number, name in enumerate(order, 1):
        print(f"{number:3}. {name}")
    for name, dep in cycles:
        print(f"цикл {name} -> {dep}: ребро пропущено, порядок "
              f"внутри цикла условный")


def show_dot(config, image, view):
    """Напечатать DOT, сохранить картинку и ASCII-дерево."""
    repo = make_repo(config)
    root = config["package"]
    graph = build_graph(repo.get_deps, root, config["max_depth"])
    dot_text = to_dot(graph, root)
    print(dot_text, end="")
    image = image or os.path.join("out", root + ".png")
    folder = os.path.dirname(image)
    if folder:
        os.makedirs(folder, exist_ok=True)
    error = render(dot_text, image)
    if error:
        print(f"картинка не создана: {error}. Текст DOT выше можно "
              f"вставить в https://dreampuf.github.io/GraphvizOnline",
              file=sys.stderr)
    else:
        print(f"картинка сохранена: {image}", file=sys.stderr)
        if view:
            webbrowser.open(Path(image).resolve().as_uri())
    if config["ascii_tree"]:
        print("\n".join(ascii_tree(graph, root)))


def main(argv=None):
    """Загрузить конфигурацию и выполнить выбранное действие."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        if args.show == "params":
            print("\n".join(config_lines(config)))
        elif args.show == "graph":
            show_graph(config)
        elif args.show == "dot":
            show_dot(config, args.image, args.view)
        elif args.show == "order":
            show_order(config)
        elif args.show == "deps":
            show_deps(config)
    except ConfigError as err:
        print(f"ошибка конфигурации: {err}", file=sys.stderr)
        return 1
    except RepoError as err:
        print(f"ошибка репозитория: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
