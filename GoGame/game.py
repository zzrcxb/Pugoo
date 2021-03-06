import json
from .group import Group
from .graph import Graph
from .final import get_final_group_prop, circle_analysis
from numpy import sign, abs
from numpy.random import randint
import numpy as np
from copy import deepcopy, copy
from config import GUI
import operator

class NoBackUpRollBackError(Exception):
    pass


class Point:
    def __init__(self, axis, color, key, num=0):
        self.x = axis[0]
        self.y = axis[1]
        self.color = color
        self.key = key
        self.num = num

    def __deepcopy__(self, memodict={}):
        p = Point([self.x, self.y], self.color, self.key, self.num)
        return p

    def tostring(self):
        return '[' + str(self.x) + ' ' + str(self.y) + ']'

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ') ' + str(self.color) + ' ' + str(self.key)


class Game:
    def __init__(self, board, _tic=False, _backup=True):
        self.board = board
        self.record = []
        self.pieces = [[Point([i, j], 0, -1) for i in range(self.board.linenum)] for j in range(self.board.linenum)]
        self.linenum = self.board.linenum
        self.pointer = 0
        self.komi = 0
        self.handicap = 0
        self.handicap_points = []
        self._pass = {1:0, -1:0}
        # Deal with group
        self.id = 0
        self.graph = Graph(True)
        self.showgroup = False
        self.robbery = []
        self.death = {1: 0, -1: 0}  # 1 for black, -1 for white
        self.result = {1: 0, -1: 0}
        # Deal with circles
        # For backup
        self.__backup__ = []
        self.__tic__ = _tic
        self.__backup = _backup
        if _tic:
            from monitor import Monitor
            self.monitor = Monitor()

    def __deepcopy__(self, memodict={}):
        g = Game(self.board, self.__tic__, self.__backup)
        g.record = self.record
        g.pieces = deepcopy(self.pieces)
        g.linenum = self.linenum
        g.pointer = self.pointer
        g.komi = self.komi
        g.handicap = self.handicap
        g.handicap_points = self.handicap_points
        g._pass = copy(self._pass)
        g.id = self.id
        g.graph = deepcopy(self.graph)
        g.showgroup = self.showgroup
        g.robbery = deepcopy(self.robbery)
        g.death = copy(self.death)
        g.result = copy(self.result)
        return g

    def clear_group(self, key):
        if self.__tic__:
            self.monitor.enter('clear_group')

        color = self.graph.nodes[key].color
        self.death[color] += len(self.graph.nodes[key].members)
        if self.showgroup and GUI:
            self.board.show_groups(self.graph.nodes[key], False)
        for a in self.graph.nodes[key].members:
            i = a.y
            j = a.x
            point = self.pieces[i][j]
            point.color = 0
            point.num = -1
            point.key = 0
            if GUI:
                self.board.remove_point([j, i])
            # Set liberties around
            for m in range(2):
                for n in range(2):
                    row = m - n + i
                    col = m + n - 1 + j
                    if row < 0 or col < 0 or row >= self.board.linenum or col >= self.board.linenum:
                        continue
                    if self.pieces[row][col].color == -color:
                        temp_key = self.pieces[row][col].key
                        self.graph.nodes[temp_key].liberties |= {(j, i), }
                        self.graph.nodes[temp_key].life = len(self.graph.nodes[temp_key].liberties)
        self.graph.remove_node(key)

        if self.__tic__:
            self.monitor.leave('clear_group')

    def clear_dead(self):
        if self.__tic__:
            self.monitor.enter('clear_dead')
        nodes = self.graph.nodes
        for key in nodes:
            nodes[key].life = len(nodes[key].liberties)

        gonna_delete = []
        self.robbery = []
        for key in self.graph.nodes:
            if not self.graph.nodes[key].protected:
                if self.graph.nodes[key].life <= 0:
                    for member in self.graph.nodes[key].members:
                        point = self.pieces[member.y][member.x]
                        point.color = 0
                        point.key = 0
                        point.num = -1
                        if GUI:
                            self.board.remove_point([member.x, member.y])
                    gonna_delete.append(key)
            else:
                self.graph.nodes[key].protected = False
                self.graph.nodes[key].attention = False
                self.robbery.append(self.graph.nodes[key])
        for key in gonna_delete:
            color = self.graph.nodes[key].color
            self.death[color] += len(self.graph.nodes[key].members)
            for a in self.graph.nodes[key].members:
                i = a.y
                j = a.x
                for m in range(2):
                    for n in range(2):
                        row = m - n + i
                        col = m + n - 1 + j
                        if row < 0 or col < 0 or row >= self.board.linenum or col >= self.board.linenum:
                            continue
                        if self.pieces[row][col].color == -color:
                            temp_key = self.pieces[row][col].key
                            self.graph.nodes[temp_key].liberties |= {(j, i), }
                            self.graph.nodes[temp_key].life = len(self.graph.nodes[temp_key].liberties)
            if self.showgroup and GUI:
                self.board.show_groups(self.graph.nodes[key], False)
            self.graph.remove_node(key)

            if self.__tic__:
                self.monitor.leave('clear_dead')

    # 3 for border
    def add_piece(self, axis, color):  # color is 1 for black, -1 for white
        return_str = ''
        i = axis[1]
        j = axis[0]
        if i == -1 and j == -1:
            self._pass[color] += 1
            return True
        if i * j == -1:
            return False
        try:
            point = self.pieces[i][j]
        except IndexError as e:
            print(e)
            print(i, j)
            return False
        _backup = Point((point.x, point.y), point.color, point.key, point.num)

        if point.color != 0:
            return False

        # Need roll back if anything goes wrong
        point.color = color
        point.num = self.pointer + 1
        if GUI:
            self.board.add_point(point)  # gui

        view = [[3 for i in range(3)] for i in range(3)]
        view[1][1] = point.color
        max_index = self.board.linenum - 1
        mycolor = view[1][1]
        border = False

        # setting up views
        if i != 0:
            view[0][1] = self.pieces[i - 1][j].color
            if i != max_index:
                view[2][1] = self.pieces[i + 1][j].color
            if j != 0:
                view[0][0] = self.pieces[i - 1][j - 1].color
                view[1][0] = self.pieces[i][j - 1].color
                if i != max_index:
                    view[2][0] = self.pieces[i + 1][j - 1].color
            if j != max_index:
                view[0][2] = self.pieces[i - 1][j + 1].color
                view[1][2] = self.pieces[i][j + 1].color
                if i != max_index:
                    view[2][2] = self.pieces[i + 1][j + 1].color
        else:
            view[0][0] = 3
            view[0][1] = 3
            view[0][2] = 3
            if i != max_index:
                view[2][1] = self.pieces[i + 1][j].color
            if j != 0:
                view[1][0] = self.pieces[i][j - 1].color
                if i != max_index:
                    view[2][0] = self.pieces[i + 1][j - 1].color
            if j != max_index:
                view[1][2] = self.pieces[i][j + 1].color
                if i != max_index:
                    view[2][2] = self.pieces[i + 1][j + 1].color

        # set same pieces
        for m in range(3):
            for n in range(3):
                if view[m][n] != 3:
                    view[m][n] *= mycolor
        # Check border
        if view[0][1] == 3 or view[1][0] == 3 or view[1][2] == 3 or view[2][1] == 3:
            border = True
        # set surround
        nearby = []
        surround = 0
        liberties = []
        cnt = 0
        for m in range(2):
            for n in range(2):
                row = m - n + i
                col = m + n - 1 + j
                if view[m + 1 - n][m + n] == 1:
                    nearby.append(self.pieces[row][col])
                    cnt += 1
                if view[m + 1 - n][m + n] != 0:
                    surround += 1
                if view[m + 1 - n][m + n] == 0:
                    liberties.append((col, row))
        # Single dot
        if cnt == 0:
            g = Group(self.id, {Point(axis, mycolor, self.id, self.pointer + 1), }, mycolor)  # new group
            g.border = border
            g.liberties = set(liberties)
            point.key = self.id
            g.life = 4 -surround
            self.id += 1
            self.graph.add_node(g, g.name)
            if g.life == 0:
                g.attention = True
            # ================Careful!!!!=================
            _neighbors = []
            # Set life
            for m in range(2):
                for n in range(2):
                    row = m - n + i
                    col = m + n - 1 + j
                    if abs(view[m + 1 - n][m + n]) == 1:
                        node = self.graph.nodes[self.pieces[row][col].key]
                        if tuple(axis) in self.graph.nodes[self.pieces[row][col].key].liberties:
                            node.liberties.remove(tuple(axis))
                            node.life = len(node.liberties)
                        _neighbors.append(self.pieces[row][col].key)
            if g.attention:
                for m in range(2):
                    for n in range(2):
                        row = m - n + i
                        col = m + n - 1 + j
                        if abs(view[m + 1 - n][m + n]) == 1:
                            key = self.pieces[row][col].key
                            if self.graph.nodes[key].life == 0:
                                if self.graph.nodes[key] in self.robbery:
                                    # Roll back
                                    for neighbor in _neighbors:
                                        self.graph.nodes[neighbor].liberties.add(tuple(axis))
                                        self.graph.nodes[neighbor].life = len(self.graph.nodes[neighbor].liberties)
                                    self.graph.remove_node(g.name)
                                    self.pieces[i][j] = _backup
                                    if GUI:
                                        self.board.remove_point((point.x, point.y))
                                    return False
                                g.protected = True
                if not g.protected:
                    for neighbor in _neighbors:
                        self.graph.nodes[neighbor].liberties.add(tuple(axis))
                        self.graph.nodes[neighbor].life = len(self.graph.nodes[neighbor].liberties)
                    self.graph.remove_node(g.name)
                    self.pieces[i][j] = _backup
                    if GUI:
                        self.board.remove_point((point.x, point.y))
                    return False
            # Set up arcs
            for m in range(2):
                for n in range(2):
                    row = i - 1 + 2 * m
                    col = j - 1 + 2 * n
                    if view[2 * m][2 * n] == 1:  # same color, create arcs
                        self.graph.add_arc(self.pieces[row][col].key, g.name)
            if self.showgroup and GUI:
                self.board.show_groups(g, True)
            return_str = ('new', )

        else:
            group_type = list(set([a.key for a in nearby]))
            # Only one dot
            if len(group_type) == 1:
                key = group_type[0]
                self.pieces[i][j].key = key
                g = self.graph.nodes[key]
                g.members.add(self.pieces[i][j])
                g.border |= border
                g.liberties |= set(liberties)
                # Set life
                _neighbors = []
                for m in range(2):
                    for n in range(2):
                        row = m - n + i
                        col = m + n - 1 + j
                        if abs(view[m + 1 - n][m + n]) == 1:
                            key = self.pieces[row][col].key
                            node = self.graph.nodes[key]
                            if tuple(axis) in self.graph.nodes[key].liberties:
                                node.liberties.remove(tuple(axis))
                                node.life = len(node.liberties)
                            _neighbors.append(key)
                if g.life == 0:
                    for m in range(2):
                        for n in range(2):
                            row = m - n + i
                            col = m + n - 1 + j
                            if abs(view[m + 1 - n][m + n]) == 1:
                                key = self.pieces[row][col].key
                                if key == g.name:
                                    continue
                                if self.graph.nodes[key].life == 0:
                                    if self.graph.nodes[key] in self.robbery:
                                        for neighbor in _neighbors:
                                            self.graph.nodes[neighbor].liberties.add(tuple(axis))
                                            self.graph.nodes[neighbor].life = len(self.graph.nodes[neighbor].liberties)
                                        self.pieces[i][j] = _backup
                                        if GUI:
                                            self.board.remove_point((point.x, point.y))
                                        return False
                                    g.protected = True
                    if not g.protected:
                        for neighbor in _neighbors:
                            self.graph.nodes[neighbor].liberties.add(tuple(axis))
                            self.graph.nodes[neighbor].life = len(self.graph.nodes[neighbor].liberties)
                        self.pieces[i][j] = _backup
                        if GUI:
                            self.board.remove_point((point.x, point.y))
                        return False
                # Link
                for m in range(2):
                    for n in range(2):
                        row = i - 1 + 2 * m
                        col = j - 1 + 2 * n
                        if view[2 * m][2 * n] == 1:  # same color, create arcs
                            self.graph.add_arc(self.pieces[row][col].key, g.name)
                # Show gui
                if self.showgroup and GUI:
                    self.board.show_groups(g, False)
                    self.board.show_groups(g, True)
                return_str = ('append', )

            # Link all nearby groups
            else:
                g = Group(self.id, {Point(axis, mycolor, self.id, self.pointer + 1), }, mycolor)  # new group
                g.border = border
                g.liberties |= set(liberties)
                self.id += 1
                self.pieces[i][j].key = g.name
                self.graph.add_node(g, g.name)
                for key in group_type:
                    for a in self.graph.nodes[key].members:
                        self.pieces[a.y][a.x].key = g.name
                        a.key = g.name
                    g.border |= self.graph.nodes[key].border
                    g.liberties |= self.graph.nodes[key].liberties

                if self.showgroup:
                    for group in group_type:
                        if GUI:
                            self.board.show_groups(self.graph.nodes[group], False)

                group_type.append(g.name)
                self.graph.combine_nodes(group_type)
                # Set link
                for m in range(2):
                    for n in range(2):
                        row = i - 1 + 2 * m
                        col = j - 1 + 2 * n
                        if view[2 * m][2 * n] == 1:  # same color, create arcs
                            self.graph.add_arc(self.pieces[row][col].key, g.name)
                # Set life
                for m in range(2):
                    for n in range(2):
                        row = m - n + i
                        col = m + n - 1 + j
                        if abs(view[m + 1 - n][m + n]) == 1:
                            key = self.pieces[row][col].key
                            node = self.graph.nodes[key]
                            if tuple(axis) in self.graph.nodes[key].liberties:
                                node.liberties.remove(tuple(axis))
                                node.life = len(node.liberties)
                '''
                if g.life == 0:
                    for m in range(2):
                        for n in range(2):
                            row = m - n + i
                            col = m + n - 1 + j
                            if abs(view[m + 1 - n][m + n]) == 1:
                                key = self.pieces[row][col].key
                                if self.graph.nodes[key].life == 0:
                                    if self.graph.nodes[key] in self.robbery:
                                        return False
                                    g.protected = True
                    if not g.protected:
                        return False
                '''
                if self.showgroup and GUI:
                    self.board.show_groups(g, True)
                group_type.append(g.name)
                return_str = ('combine', group_type)

        self.clear_dead()
        # if self.showgroup:
        #     print('=====', self.pointer, '====')
        #     self.graph.print()
        return return_str

    def circle_analysis(self):
        self.circles = circle_analysis(self.graph, self.board.linenum)

    def remove_dead(self, debug=False, color=None):
        if self.__tic__:
            self.monitor.enter('remove dead')
            self.monitor.enter('circle_analysis')
        self.circle_analysis()
        if self.__tic__:
            self.monitor.leave('circle_analysis')
        black_enclosed = set()
        white_enclosed = set()
        suspicious = []
        _gonna_remove = []
        in_circles = {}
        for key in self.circles.circles:
            circle = self.circles.circles[key]
            for member in circle.members:
                if member in in_circles:
                    in_circles[member].append(key)
                else:
                    in_circles[member] = [key, ]
            if circle.color == 1:
                black_enclosed = black_enclosed | circle.enclosed
            else:
                white_enclosed = white_enclosed | circle.enclosed
        enclosed = {1:black_enclosed, -1:white_enclosed}
        # Set eyes
        nodes = self.graph.nodes
        arc = self.graph.arcs
        # for key in in_circles:
        #     nodes[key].eyes += len(in_circles[key])
        # With all enclosed points are set
        for key in nodes:
            node = nodes[key]
            members = {(point.x, point.y) for point in node.members}
            if members.issubset(enclosed[-node.color]):
                if node.eyes == 0 and node.lines < 2:
                    _gonna_remove.append(key)
                elif node.life < 2:
                    _gonna_remove.append(key)
                elif node.eyes <= 1:
                    suspicious.append(key)
        if not color:
            for _ in _gonna_remove:
                if nodes[_] not in self.robbery:
                    self.clear_group(_)
        else:
            suspicious.extend(_gonna_remove)
        if debug:
            print("Suspicious", suspicious)
            print("Gonna remove", _gonna_remove)
        if self.__tic__:
            self.monitor.leave('remove dead')
        return suspicious, len(_gonna_remove)

    def remover(self, debug=False):
        if debug:
            cnt = 0
        while 1:
            if debug:
                print("======", cnt, "======")
                cnt += 1
            suspicious, size = self.remove_dead(debug)
            # game = self.__deepcopy__()
            _gonna_delete = self.check_suspicious(suspicious)
            a = [[self.pieces[i][j].key for j in range(19)] for i in range(19)]
            for key in _gonna_delete:
                self.clear_group(key)
            if size == 0:
                break

    def get_liberties(self, axis):
        j, i = axis
        sur = 0
        nearby = []
        if i < 0 or j < 0 or i >= self.linenum or j >= self.linenum:
            return None
        for m in range(2):
            for n in range(2):
                row = m - n + i
                col = m + n - 1 + j
                if row < 0 or col < 0 or row >= self.linenum or col >= self.linenum:
                    sur += 1
                elif abs(self.pieces[row][col].color) == 1:
                    sur += 1
                elif self.pieces[row][col].color == 0:
                    nearby.append((col, row))
        return 4 - sur, nearby

    def set_final_group_prop(self):
        if self.__tic__:
            self.monitor.enter('set final group')

        for key in self.graph.nodes:
            group = self.graph.nodes[key]
            res = get_final_group_prop(group, self.board.linenum)
            group.sizex = res['sx']
            group.sizey = res['sy']
            group.size = res['size']
            group.eyes = res['eyes']
            group.mass_core = res['mass_core']

        if self.__tic__:
            self.monitor.leave('set final group')

    def score_final(self, debug=False):
        if self.__tic__:
            self.monitor.enter('score final')
        linenum = self.board.linenum
        points = [[self.pieces[i][j].color for j in range(linenum)] for i in range(linenum)]
        pieces = np.array(points)
        pieces = np.pad(pieces, ((1, ), (1, )), mode='constant', constant_values=3)

        black_points = np.count_nonzero(pieces == 1)
        white_points = np.count_nonzero(pieces == -1)
        # print(pieces)
        _pieces = deepcopy(pieces)  # Apply changes on _pieces
        dim = linenum + 2
        while 1:
            ones = np.array(np.where(pieces == 1)).transpose()  # black points
            ones = list(map(list, ones))
            n_ones = np.array(np.where(pieces == -1)).transpose()  # white points
            n_ones = list(map(list, n_ones))
            ones.extend(n_ones)
            abs_ones = ones
            for i, j in abs_ones:
                mycolor = _pieces[i][j]
                # Set points
                for m in range(2):
                    for n in range(2):
                        row = m - n + i
                        col = m + n - 1 + j
                        if _pieces[row][col] == - mycolor * 2:  # Neutral point
                            _pieces[row][col] = 4  # 4 for neutral
                        if _pieces[row][col] == 0:
                            _pieces[row][col] = mycolor * 2
            _pieces[_pieces == 2] = 1
            _pieces[_pieces == -2] = -1
                # Compare
            if abs(_pieces - pieces).sum() == 0:
                break
            pieces = _pieces
            _pieces = deepcopy(pieces)

        pieces = _pieces[1:dim - 1, 1:dim -1]
        white = np.count_nonzero(pieces == -1)
        black = np.count_nonzero(pieces == 1)
        neutral = np.count_nonzero(pieces == 4)
        half = int(neutral / 2)
        n_w = 0
        n_b = 0
        # if neutral % 2 == 1:
        #     if len(self.record) % 2 == 1:
        #         n_w += 1
        #     else:
        #         n_b += 1
        self.result[1] = black + n_b
        self.result[-1] = white  + self.komi + n_w
        if self.handicap != 0:
            self.result[-1] += self.handicap - 1
        if debug:
            print(dict(komi=self.komi, handicap=self.handicap))
            print("Result", dict(b=self.result[1], w=self.result[-1]))
            print("Areas", dict(b=black, w=white))
            print("Territory", dict(b=black - black_points, w=white - white_points))
            print("Death", dict(b=self.death[1], w=self.death[-1]))

        if self.showgroup and GUI:
            self.board.show_territory(pieces)
        if self.__tic__:
            self.monitor.leave('score final')
        return self.result[1] - self.result[-1]

    def backup(self):
        if self.__tic__:
            self.monitor.enter('backup')
        self.__backup__.append([deepcopy(self.pieces), deepcopy(self.graph)])
        if self.__tic__:
            self.monitor.leave('backup')

    def restore(self):
        self.pieces = self.__backup__[-1][0]
        self.graph = self.__backup__[-1][1]
        for i in range(len(self.robbery)):
            key = self.robbery[i].name
            self.robbery[i] = self.graph.nodes[key]

    def cal_single(self, axis):
        i = axis[1]
        j = axis[0]
        view = []
        me = self.pieces[i][j]
        mycolor = me.color
        pieces = np.array([[piece.color for piece in row] for row in self.pieces])
        if mycolor == 1:
            np.pad(pieces, ((2, ), (2, )), mode='constant', constant_values=-1)
            view = pieces[i: i + 5, j: j + 5]
        elif mycolor == -1:
            np.pad(pieces, ((2,), (2,)), mode='constant', constant_values=1)
            view = pieces[i: i + 5, j: j + 5]
            view = -view
        sums = np.sum(view)
        key = me.key
        size = len(self.graph.nodes[key].members)
        life = self.graph.nodes[key].life

        return sums, size, life, mycolor

    def res_clear(self):
        for key in self.graph.nodes:
            node = self.graph.nodes[key]
            if len(node.members) < 10:
                sum = [[], [], []]
                for piece in node.members:
                    res = self.cal_single([piece.x, piece.y])
                    sum[0].append(res[0])
                    sum[1].append(res[1])
                    sum[2].append(res[2])
                print(node.name, np.average(np.array(sum[0])), np.average(np.array(sum[1])), np.average(np.array(sum[2])))

    def random_play(self, fail=30):
        max_fail = 0
        linenum = self.board.linenum
        while max_fail < fail:
            axis = list(randint(linenum, size=2))
            axis[0] = int(axis[0])
            axis[1] = int(axis[1])
            if not self.add_point(axis, 1):
                max_fail += 1
            else:
                max_fail = 0
                self.record.append(axis)
                self.pointer += 1
        print("Done")
        self.save_game('test', r'D:\Users\Neil Zhao\Desktop\go2\test.bg')

    def add_point(self, axis, color):
        # logic
        if self.__backup:
            self.backup()
        return self.add_piece(axis, color)

    def next_step(self):
        if self.pointer < len(self.record):
            if self.__backup:
                self.backup()
            # logic
            axis = self.record[self.pointer][0:2]
            color = self.record[self.pointer][2]
            if self.__tic__:
                self.monitor.enter('add_piece')
            if self.add_piece(axis, color):
                self.pointer += 1
            else:
                return False
            if self.__tic__:
                self.monitor.leave('add_piece')
            return True

    def prev_step(self):
        print(self.pointer)
        if self.pointer > 0:
            self.pointer -= 1
            axis = list(self.record[self.pointer])
            # gui
            if GUI:
                self.board.remove_point(axis)
            # logic
            self.restore()

    def goto(self, step):
        max = len(self.record)
        if step > max or step < 0:
            return True
        while self.pointer != step:
            if step < self.pointer:
                self.prev_step()
            else:
                if not self.next_step():
                    return None
        return True

    def load_game(self, path):
        with open(path, 'r') as out:
            j = json.load(out)
        self.record = j['record']
        self.komi = j["attrs"]['KM']
        self.handicap = j["attrs"]['HA']
        self.handicap_points = j['handicap']
        if self.handicap != 0:  # Place handicap
            for axis in self.handicap_points:
                if self.__backup__:
                    self.backup()
                if not self.add_piece(axis, 1):
                    try:
                        if GUI:
                            self.board.remove_point(axis)
                    except:
                        pass
                    if self.__backup__:
                        self.restore()
                    else:
                        raise NoBackUpRollBackError()

    def save_game(self, name, path):
        print(dict(name=name, record=self.record))
        with open(path, 'w') as out:
            json.dump(dict(name=name, record=self.record), out)

    def show_groups(self):
        self.showgroup = not self.showgroup
        if not self.showgroup:
            self.board.show_groups(None, False)
            # self.board.show_territory(None, False)

    def check_suspicious(self, suspicious, _max=50):
        game = Game(self.board, _backup=False)
        game.pieces = deepcopy(self.pieces)
        game.graph = deepcopy(self.graph)
        game.showgroup = self.showgroup
        game.robbery = deepcopy(self.robbery)
        game.record = deepcopy(self.record)
        game.id = self.id
        graph = game.graph
        _gonna_delete = []
        ws = set()
        bs = set()
        for key in suspicious:
            if graph.nodes[key].color == 1:  # Black group
                bs.add(key)
            elif graph.nodes[key].color == -1:  # White group
                ws.add(key)
        dominant = - game.record[-1][-1]
        suspicious = {1: ws, -1: bs}
        while len(suspicious[1]) > 0 or len(suspicious[-1]) > 0 and _max > 0:
            cnt = 0
            # Attack
            nominees = {}
            FLAG = True
            dying = {}
            for key in suspicious[dominant]:
                if graph.nodes[key].life == 1:  # Dying
                    dying[key] = len(graph.nodes[key].members)
                for point in graph.nodes[key].liberties:
                    point = tuple(point)
                    nominees[point] = nominees.get(point, 0) + 1
            while len(dying) > 0:
                key = max(dying.items(), key=operator.itemgetter(1))[0]
                (_point,) = graph.nodes[key].liberties
                feedback = game.add_point(_point, dominant)
                if not feedback:  # Invalid move
                    del dying[_point]
                elif feedback[0] == 'combine':
                    for removed in feedback[1][0: -1]:
                        if removed in suspicious[-dominant]:
                            suspicious[-dominant].remove(removed)
                            suspicious[-dominant].add(feedback[1][-1])
                    FLAG = False
                    cnt += 1
                    break  # Success
                else:
                    FLAG = False
                    cnt += 1
                    break  # Success
            while len(nominees) > 0 and FLAG:
                _point = max(nominees.items(), key=operator.itemgetter(1))[0]
                feedback = game.add_point(_point, dominant)
                if not feedback:  # Invalid move
                    del nominees[_point]
                elif feedback[0] == 'combine':
                    for removed in feedback[1][0: -1]:
                        if removed in suspicious[-dominant]:
                            suspicious[-dominant].remove(removed)
                            suspicious[-dominant].add(feedback[1][-1])
                    cnt += 1
                    break
                else:
                    cnt += 1
                    break  # Success
            # Check if exists
            new_removed = []
            for key in suspicious[dominant]:
                if key not in graph.nodes:
                    _gonna_delete.append(key)
                    new_removed.append(key)
            for key in new_removed:
                suspicious[dominant].remove(key)
            # Defense
            # Clean dying
            FLAG = True
            dying = {}
            for key in graph.nodes:
                if graph.nodes[key].life == 1 and graph.nodes[key].color == dominant:  # Dying
                    dying[key] = len(graph.nodes[key].members)
            while len(dying) > 0:
                key = max(dying.items(), key=operator.itemgetter(1))[0]
                (_point,) = graph.nodes[key].liberties
                feedback = game.add_point(_point, -dominant)
                if not feedback:  # Invalid move
                    del dying[key]
                elif feedback[0] == 'combine':
                    for removed in feedback[1][0: -1]:
                        if removed in suspicious[dominant]:
                            suspicious[dominant].remove(removed)
                            suspicious[dominant].add(feedback[1][-1])
                    cnt += 1
                    FLAG = False
                    break
                else:
                    FLAG = False
                    cnt += 1
                    break  # Success

            lifes = {key: graph.nodes[key].life for key in suspicious[dominant]}
            while len(lifes) > 0 and FLAG:
                key = min(lifes.items(), key=operator.itemgetter(1))[0]
                nominees = {}
                for _point in graph.nodes[key].liberties:
                    predict = game.get_liberties(_point)
                    already = [i for i in predict[1] if i in graph.nodes[key].liberties]
                    extend_life = predict[0] - 1 - len(already)
                    nominees[_point] = extend_life
                while len(nominees) > 0:
                    best = max(nominees.items(), key=operator.itemgetter(1))
                    if best[1] > 0:
                        feedback = game.add_point(best[0], -dominant)
                        if not feedback:  # Invalid move
                            del nominees[best[0]]
                        elif feedback[0] == 'combine':
                            for removed in feedback[1][0: -1]:
                                if removed in suspicious[dominant]:
                                    suspicious[dominant].remove(removed)
                                    suspicious[dominant].add(feedback[1][-1])
                            FLAG = False
                            cnt += 1
                            break
                        else:
                            FLAG = False
                            cnt += 1
                            break  # Success
                    else:
                        break
                if FLAG:
                    del lifes[key]

            _suspicious, size = game.remove_dead(color=-dominant)
            suspicious = {1: set(), -1: set()}
            for key in _suspicious:
                if graph.nodes[key].color == 1:  # Black group
                    suspicious[-1].add(key)
                elif graph.nodes[key].color == -1:  # White group
                    suspicious[1].add(key)

            _max -= 1
            if len(suspicious[dominant]) == 0:
                dominant = -dominant
            if cnt == 0:
                break
        # Recovery
        return _gonna_delete
