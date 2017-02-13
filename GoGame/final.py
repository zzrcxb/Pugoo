import numpy as np
from .circle import Circle, Circles
from .group import Group
from copy import deepcopy


def get_group_mass_core(group):
    xs = [p.x for p in group.members]
    ys = [p.y for p in group.members]
    mass_core = sum(xs) / len(xs), sum(ys) / len(ys)
    return mass_core


def get_final_group_prop(group, line_num, members=None):  # (mass core, number, eyes, sizex, sizey)
    xs = [p.x for p in group.members]
    ys = [p.y for p in group.members]
    sizex = min(xs), max(xs)
    sizey = min(ys), max(ys)
    dimx = sizex[1] - sizex[0] + 1
    dimy = sizey[1] - sizey[0] + 1

    number = len(group.members)
    mass_core = sum(xs) / len(xs), sum(ys) / len(ys)

    # Gonna deal with eyes
    eyes_cnt = 0
    points = [(p.x - sizex[0], p.y - sizey[0]) for p in group.members]
    window = np.zeros((dimy, dimx))
    for p in points:
        window[p[1]][p[0]] = 1
    window = np.pad(window, ((1,), (1,)), mode='constant', constant_values=2)
    # Set up border judge
    circles = Circles()
    borders = [False, False, False, False]  # Up, left, right, down
    if sizey[0] == 0:
        borders[0] = True
    if sizex[0] == 0:
        borders[1] = True
    if sizex[1] == line_num - 1:
        borders[2] = True
    if sizey[1] == line_num - 1:
        borders[3] = True
    # Walk
    while 1:
        pos = np.where(window == 0)
        if pos[0].size == 0:
            break
        adjacent = [False, False, False, False]
        enclosed = []
        count_one_eye(window, adjacent, pos[1][0], pos[0][0], enclosed, [sizex[0], sizey[0]])
        flag = True
        for i in range(4):
            if adjacent[i]:
                if not borders[i]:
                    flag = False
                    break
        if flag:
            eyes_cnt += 1
            if not members:
                circle = Circle({group.name, }, enclosed, group.color, hash(tuple(enclosed)), (sizex, sizey), 'internal')
            else:
                circle = Circle(set(members), enclosed, group.color, hash(tuple(enclosed)), (sizex, sizey), 'internal')
            circles.append(circle)

    return dict(mass_core=mass_core, size=number, eyes=eyes_cnt, sx=sizex, sy=sizey, circles=circles)


def count_one_eye(window, adj, x, y, enclosed, min):
    window[y][x] = -1
    enclosed.append((x - 1 + min[0], y - 1 + min[1]))
    # Go up
    if window[y - 1][x] == 0:
        count_one_eye(window, adj, x, y - 1, enclosed, min)
    elif window[y - 1][x] == 2:  # Border
        adj[0] = True

    # Go left
    if window[y][x - 1] == 0:
        count_one_eye(window, adj, x - 1, y, enclosed, min)
    elif window[y][x - 1] == 2:  # Border
        adj[1] = True

    # Go right
    if window[y][x + 1] == 0:
        count_one_eye(window, adj, x + 1, y, enclosed, min)
    elif window[y][x + 1] == 2:  # Border
        adj[2] = True

    # Go down
    if window[y + 1][x] == 0:
        count_one_eye(window, adj, x, y + 1, enclosed, min)
    elif window[y + 1][x] == 2:  # Border
        adj[3] = True
    return


def circle_analysis(_graph, linenum):
    nodes = _graph.nodes
    arcs = _graph.arcs
    arc_num = _graph.arc_num
    circles = Circles()
    # Internal circles
    for node_key in nodes:
        cs = get_final_group_prop(nodes[node_key], linenum)
        nodes[node_key].mass_core = cs['mass_core']
        nodes[node_key].sx = cs['sx']
        nodes[node_key].sy = cs['sy']
        nodes[node_key].size = cs['size']
        nodes[node_key].eyes = cs['eyes']
        circles.extend(cs['circles'])

    # Set lines
    for _key in nodes:
        if nodes[_key].border:
            nodes[_key].lines += 1
    # Set copy
    graph = deepcopy(_graph)

    # Out circles
    while 1:
        _gonna_remove = []
        for _key in graph.nodes:
            if graph.nodes[_key].lines <= 1:
                graph.nodes[_key].lines -= 1
                for arc_key in graph.arcs[_key]:
                    graph.nodes[arc_key].lines -= 1
                _gonna_remove.append(_key)
        if len(_gonna_remove) == 0:
            break
        for _key in _gonna_remove:
            graph.remove_node(_key)

    big_group = graph.group_dfs()
    _ = 0
    for _g in big_group:
        group = Group(_, set(), graph.nodes[_g[0]].color)
        for key in _g:
            group.combine(graph.nodes[key])
        cs = get_final_group_prop(group, linenum, members=_g)['circles']
        circles.extend(cs)
        _ += 1

    # Deal with two elem circles
    for node_key in arc_num:
        node = arc_num[node_key]
        for key in node:
            if node[key] > 1:
                n1 = nodes[node_key]
                n2 = nodes[key]
                temp = Group(0, n1.members | n2.members, n1.color)
                cs = get_final_group_prop(temp, linenum, members={node_key, key})['circles']
                circles.extend(cs)

    black_circles = []
    white_circles = []
    # Classify
    for key in circles.circles:
        if circles.circles[key].color == 1:
            black_circles.append(key)
        elif circles.circles[key].color == -1:
            white_circles.append(key)
    # Remove overlapped points
    cs = circles.circles
    for w_key in white_circles:
        for b_key in black_circles:
            if cs[w_key].enclosed.issubset(cs[b_key].enclosed):
                cs[b_key].enclosed -= cs[w_key].enclosed
            if cs[b_key].enclosed.issubset(cs[w_key].enclosed):
                cs[w_key].enclosed -= cs[b_key].enclosed
    return circles
