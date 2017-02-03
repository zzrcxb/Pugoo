import tkinter as tk


class Piece:
    def __init__(self, num, oval, text):
        self.num = num
        self.oval = oval
        self.text = text
        self.color = -(num % 2) * 2 + 1


# We use 0 for available, -1 for white, -2 for white space, 1 for black, 2 for black space
class ChessBoard:
    def __init__(self, root, pos, dis, linenum=19):
        self.dim = dis * (linenum - 1)
        self.grids = tk.Canvas(root, width=self.dim + 60, height=self.dim + 60, bd=0, bg='#ffe698')
        self.grids.pack()
        self.distance = dis
        self.grids.create_rectangle(pos[0], pos[1], pos[0] + self.dim, pos[1] + self.dim)
        self.linenum = linenum
        self.pos = pos
        self.pieces_canvas = [[None for i in range(linenum)] for i in range(linenum)]
        self.create_array()
        self.groups = {}
        self.colors = ['#FF0000', '#FFD700', '#00FFFF', '#F0F8FF', '#003366',
                       '#000080', '#E32636', '#00FF80', '#FF2400', '#FFFF00',
                       '#007FFF', '#30D5C8', '#2A52BE', '#5E86C1', '#FF00FF',
                       '#008080', '#FF4D00', '#CCFF00', '#0000FF', '#6495ED',
                       '#0047AB', '#CCCCFF', '#800000', '#000080', '#FFA500',
                       '#66FF00', '#7FFFD4', '#003399', '#1E90FF', '#082567',
                       '#FFCC00', '#4B0080', '#FFBF00', '#00FF00', '#E0FFFF',
                       '#4169E1', '#002FA7', '#8B00FF', '#808000']
        self.color_pointer = 0

    def show_groups(self, group, show):
        if show:
            while 1:
                color = self.colors[self.color_pointer]
                if group.color == -1:
                    distance = compare_color(color, '#FFFFFF')
                else:
                    distance = compare_color(color, '#000000')
                if distance > 200:
                    # print(distance, group.name, group.color, color)
                    break
                else:
                    self.color_pointer += 1
                    self.color_pointer %= len(self.colors)
            handle = []
            for member in group.members:
                x = self.cross[0][member.x]
                y = self.cross[1][member.y]
                text = self.grids.create_text(x, y, text=str(group.name), fill=color)
                handle.append(text)
            self.color_pointer += 1
            self.color_pointer %= len(self.colors)
            self.groups[group.name] = handle
        else:
            for text in self.groups[group.name]:
                self.grids.delete(text)

    def create_array(self):
        self.cross = []
        temp = []
        for i in range(self.dim):
            temp.append(self.pos[0] + i * self.distance)
        self.cross.append(temp)

        for i in range(self.dim):
            temp.append(self.pos[1] + i * self.distance)
        self.cross.append(temp)

    def drawline(self, num, vertical=False):
        if vertical:
            x = self.cross[0][num]
            self.grids.create_line(x, self.pos[1], x, self.pos[1] + self.dim)
        else:
            y = self.cross[1][num]
            self.grids.create_line(self.pos[0], y, self.pos[0] + self.dim, y)
            self.grids.update()

    def create_board(self):
        i = 0
        while i <= self.linenum:
            self.drawline(i, False)
            self.drawline(i, True)
            i += 1
        if self.linenum == 19:
            radius = self.distance * 0.1
            for i in range(3):
                for j in range(3):
                    x = self.cross[0][3 + 6 * i]
                    y = self.cross[1][3 + 6 * j]
                    self.grids.create_oval(x - radius, y -radius,
                        x + radius, y + radius, fill='black')

    def clear(self):
        for oneline in self.pieces_canvas:
            for piece in oneline:
                self.grids.delete(piece.oval)
                self.grids.delete(piece.text)
        self.grids.update()
        self.pieces_canvas = [[None for i in range(self.linenum)] for i in range(self.linenum)]

    def remove_point(self, axis):
        x = axis[0]
        y = axis[1]
        piece = self.pieces_canvas[x][y]
        if piece is not None:
            self.grids.delete(piece.oval)
            self.grids.delete(piece.text)
            self.grids.update()
            self.pieces_canvas[x][y] = None

    def add_point(self, axis, num, ratio):
        x = self.cross[0][axis[0]]
        y = self.cross[1][axis[1]]
        radius = ratio * self.distance
        padding = 0

        if num % 2 == 1:
            oval = self.grids.create_oval(x - radius, y - radius, 
                x + radius, y + radius, fill='black')
            text = self.grids.create_text(x, y, text=str(num), fill='black')
        else:
            oval = self.grids.create_oval(x - radius, y - radius, 
                x + radius, y + radius, fill='white')
            text = self.grids.create_text(x, y, text=str(num), fill='white')
        self.grids.update()
        self.pieces_canvas[axis[0]][axis[1]] = Piece(num, oval, text)

def compare_color(c1, c2):
    from math import sqrt
    r1 = int(c1[1:3], base=16)
    g1 = int(c1[3:5], base=16)
    b1 = int(c1[5:7], base=16)
    r2 = int(c2[1:3], base=16)
    g2 = int(c2[3:5], base=16)
    b2 = int(c2[5:7], base=16)

    return sqrt((r1 - r2) ** 2 + (b1 - b2) ** 2 + (g1 - g2) ** 2)
