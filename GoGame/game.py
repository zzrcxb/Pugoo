import json
from .group import Group
from .graph import Graph
from numpy import sign, abs
from numpy.random import randint
import numpy as np
from copy import deepcopy


class Point:
    def __init__(self, axis, color, key):
        self.x = axis[0]
        self.y = axis[1]
        self.color = color
        self.key = key

    def tostring(self):
        return '[' + str(self.x) + ' ' + str(self.y) + ']'

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ') ' + str(self.color) + ' ' + str(self.key)


class Game:
    def __init__(self, board):
        self.board = board
        self.record = []
        self.pieces = [[Point([i, j], 0, -1) for i in range(self.board.linenum)] for j in range(self.board.linenum)]
        self.pointer = 0
        self.komi = 0
        self.handicap = 0
        # Deal with group
        self.id = 0
        self.graph = Graph(True)
        self.showgroup = False
        self.robbery = []
        # For backup
        self.__backup__ = []

    def clear_dead(self):
        gonna_delete = []
        self.robbery = []
        for key in self.graph.nodes:
            if not self.graph.nodes[key].protected:
                if self.graph.nodes[key].life <= 0:
                    for member in self.graph.nodes[key].members:
                        self.pieces[member.y][member.x].color = 0
                        self.board.remove_point([member.x, member.y])
                    gonna_delete.append(key)
            else:
                self.graph.nodes[key].protected = False
                self.graph.nodes[key].attention = False
                self.robbery.append(self.graph.nodes[key])
        for key in gonna_delete:
            color = self.graph.nodes[key].color
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
                            self.graph.nodes[temp_key].life += 1
            if self.showgroup:
                self.board.show_groups(self.graph.nodes[key], False)
            self.graph.remove_node(key)

    # 3 for border
    def add_piece(self, axis):
        i = axis[1]
        j = axis[0]
        if self.pieces[i][j].color != 0:
            return False
        self.pieces[i][j].color = -(self.pointer % 2) * 2 + 1  # Black -1, white 1
        view = [[3 for i in range(3)] for i in range(3)]
        view[1][1] = self.pieces[i][j].color
        max_index = self.board.linenum - 1
        mycolor = view[1][1]

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
        # set surround
        nearby = []
        surround = 0
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
        # Single dot
        if cnt == 0:
            g = Group(self.id, {Point(axis, mycolor, self.id), }, mycolor)  # new group
            self.pieces[i][j].key = self.id
            self.id += 1
            self.graph.add_node(g, g.name)
            g.life = 4 - surround
            if g.life == 0:
                g.attention = True
            # Careful!!!!=================
            for m in range(2):
                for n in range(2):
                    row = i - 1 + 2 * m
                    col = j - 1 + 2 * n
                    if view[2 * m][2 * n] == 1:  # same color, create arcs
                        self.graph.add_arc(self.pieces[row][col].key, g.name)
            for m in range(2):
                for n in range(2):
                    row = m - n + i
                    col = m + n - 1 + j
                    if abs(view[m + 1 - n][m + n]) == 1:
                        self.graph.nodes[self.pieces[row][col].key].life -= 1
            if g.attention:
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
            if self.showgroup:
                self.board.show_groups(g, True)

        else:
            group_type = list(set([a.key for a in nearby]))
            # Only one dot
            if len(group_type) == 1:
                key = group_type[0]
                self.pieces[i][j].key = key
                self.graph.nodes[key].members.add(self.pieces[i][j])
                self.graph.nodes[key].life += 4 - surround
                g = self.graph.nodes[key]
                # Link
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
                            self.graph.nodes[key].life -= 1
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
                if self.showgroup:
                    self.board.show_groups(g, False)
                    self.board.show_groups(g, True)

            # Link all nearby groups
            else:
                g = Group(self.id, {Point(axis, mycolor, self.id), }, mycolor)  # new group
                g.life = 4 - surround
                self.id += 1
                self.pieces[i][j].key = g.name
                self.graph.add_node(g, g.name)
                for key in group_type:
                    for a in self.graph.nodes[key].members:
                        self.pieces[a.y][a.x].key = g.name
                        a.key = g.name
                    self.graph.nodes[g.name].life += self.graph.nodes[key].life
                if self.showgroup:
                    for group in group_type:
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
                            self.graph.nodes[key].life -= 1
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
                if self.showgroup:
                    self.board.show_groups(g, True)

        self.clear_dead()
        # if self.showgroup:
        #     print('=====', self.pointer, '====')
        #     self.graph.print()
        return True

    def backup(self):
        self.__backup__.append([deepcopy(self.pieces), deepcopy(self.graph)])

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
            if not self.add_point(axis):
                max_fail += 1
            else:
                max_fail = 0
                self.record.append(axis)
                self.pointer += 1
        print("Done")
        self.save_game('test', r'D:\Users\Neil Zhao\Desktop\go2\test.bg')

    def add_point(self, axis):
        if axis[0] == -1 and axis[1] == -1:
            return True
        elif axis[0] == -1 or axis[1] == -1:
            return False
        # gui
        # self.board.add_point(axis, self.pointer + 1, 0.4)
        # logic
        self.backup()
        if self.add_piece(axis):
            return True
        else:
            # self.board.remove_point(axis)
            self.restore()
            return False

    def next_step(self):
        if self.pointer < len(self.record):
            axis = list(self.record[self.pointer])
            # gui
            self.board.add_point(axis, self.pointer + 1, 0.4)
            # logic
            self.backup()
            if self.add_piece(axis):
                self.pointer += 1
            else:
                self.board.remove_point(axis)
                self.restore()

    def prev_step(self):
        print(self.pointer)
        if self.pointer > 0:
            self.pointer -= 1
            axis = list(self.record[self.pointer])
            # gui
            self.board.remove_point(axis)
            # logic
            self.restore()

    def goto(self, step):
        max = len(self.record)
        if step > max or step < 0:
            return
        while self.pointer != step:
            if step < self.pointer:
                self.prev_step()
            else:
                self.next_step()

    def load_game(self, path):
        with open(path, 'r') as out:
            j = json.load(out)
        self.record = j['record']
        self.name = j['name']

    def save_game(self, name, path):
        print(dict(name=name, record=self.record))
        with open(path, 'w') as out:
            json.dump(dict(name=name, record=self.record), out)

    def show_groups(self):
        self.showgroup = not self.showgroup
        if not self.showgroup:
            self.board.show_groups(self.graph, False)

    def test(self):
        num = 1
        for i in range(self.board.linenum):
            for j in range(self.board.linenum):
                self.board.add_point((i, j), num, 0.4)
                self.pieces[j][i] = -(num % 2) * 2 + 1
                num += 1
                self.record.append([i, j])
        self.pointer = len(self.record)
