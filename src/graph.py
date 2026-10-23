"""Построение графа зависимостей и операции над ним."""

GRAY = "gray"    # вершина в текущем пути обхода
BLACK = "black"  # вершина полностью обработана


def build_graph(get_deps, root, max_depth):
    """Построить граф обходом DFS без рекурсии, на явном стеке.

    get_deps(имя) возвращает список прямых зависимостей. Результат -
    словарь {пакет: [зависимости]} для раскрытых пакетов. Пакеты на
    глубине max_depth не раскрываются и есть только среди
    зависимостей. Повторно пакет раскрывается, только если найден
    более короткий путь к нему, поэтому циклы не зацикливают обход.
    """
    graph = {}
    depth_of = {}
    stack = [(root, 0)]
    while stack:
        name, depth = stack.pop()
        if name in depth_of and depth_of[name] <= depth:
            continue
        depth_of[name] = depth
        if depth == max_depth:
            continue
        if name not in graph:
            graph[name] = get_deps(name)
        # В обратном порядке, чтобы первой обошлась первая зависимость.
        for dep in reversed(graph[name]):
            stack.append((dep, depth + 1))
    return graph


def all_nodes(graph):
    """Вернуть все пакеты графа, включая нераскрытые листья."""
    nodes = list(graph)
    for deps in graph.values():
        nodes.extend(dep for dep in deps if dep not in nodes)
    return nodes


def walk(graph, root):
    """Обойти граф DFS без рекурсии.

    Возвращает (postorder, back_edges): пакеты в порядке завершения
    обхода (зависимости раньше зависящих) и обратные ребра,
    каждое из которых замыкает цикл.
    """
    order = []
    back_edges = []
    color = {root: GRAY}
    stack = [(root, iter(graph.get(root, [])))]
    while stack:
        name, deps = stack[-1]
        dep = next(deps, None)
        if dep is None:
            stack.pop()
            color[name] = BLACK
            order.append(name)
        elif dep not in color:
            color[dep] = GRAY
            stack.append((dep, iter(graph.get(dep, []))))
        elif color[dep] == GRAY:
            back_edges.append((name, dep))
    return order, back_edges


def load_order(graph, root):
    """Вернуть порядок загрузки: зависимости раньше зависящих.

    Это топологическая сортировка через postorder обхода DFS.
    Если в графе есть цикл, обратное ребро пропускается и порядок
    внутри цикла условный, о чем сообщает второй элемент ответа.
    """
    order, back_edges = walk(graph, root)
    return order, back_edges
