import numpy as np
from .circle import Circle, Circles
from copy import deepcopy

def get_final_group_prop(group, line_num):  # (mass core, number, eyes, sizex, sizey)
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
    borders = [False, False, False, False]  # Up, left, right, down
    if sizey[0] == 0:
        borders[0] = True
    if sizex[0] == 0:
        borders[1] = True
    if sizex[1] == line_num - 1:
        borders[2] = True
    if sizey[0] == line_num - 1:
        borders[3] = True
    # Walk
    while 1:
        pos = np.where(window == 0)
        if pos[0].size == 0:
            break
        adjacent = [False, False, False, False]
        count_one_eye(window, adjacent, pos[1][0], pos[0][0])
        flag = True

        for i in range(4):
            if adjacent[i]:
                if not borders[i]:
                    flag = False
                    break
        if flag:
            eyes_cnt += 1
    return dict(mass_core=mass_core, size=number, eyes=eyes_cnt, sx=sizex, sy=sizey)


def count_one_eye(window, adj, x, y):
    window[y][x] = -1
    # Go up
    if window[y - 1][x] == 0:
        count_one_eye(window, adj, x, y - 1)
    elif window[y - 1][x] == 2:  # Border
        adj[0] = True

    # Go left
    if window[y][x - 1] == 0:
        count_one_eye(window, adj, x - 1, y)
    elif window[y][x - 1] == 2:  # Border
        adj[1] = True

    # Go right
    if window[y][x + 1] == 0:
        count_one_eye(window, adj, x + 1, y)
    elif window[y][x + 1] == 2:  # Border
        adj[2] = True

    # Go down
    if window[y + 1][x] == 0:
        count_one_eye(window, adj, x, y + 1)
    elif window[y + 1][x] == 2:  # Border
        adj[3] = True
    return


def circle_analysis(graph):
    nodes = deepcopy(graph.nodes)
    arcs = graph.arcs
    arc_num = graph.arc_num
    circles = Circles()
    # Deal with two elem circles
    for node_key in arc_num:
        node = arc_num[node_key]
        for key in node:
            if node[key] > 1:
                n1 = nodes[node_key]
                n2 = nodes[key]
                range = (min(n1.sizex[0], n2.sizex[0]), max(n1.sizex[1], n2.sizex[1]),
                         min(n1.sizey[0], n2.sizey[0]), max(n1.sizey[1], n2.sizey[1]))
                circles.append(Circle({node_key, key}, range))

    for node in nodes:
        pass
    return circles


if __name__ == '__main__':
    class point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    from group import Group
    p = {point(0, 1), point(1, 1), point(2, 0), point(2, 1), point(2, 2),
         point(3, 2), point(4, 2), point(5, 2), point(5, 1), point(5, 0),
         point(2, 3), point(2, 4), point(3, 4), point(4, 4), point(4, 3)}
    g = Group('he', p, 1)
    print(get_final_group_prop(g, 19))