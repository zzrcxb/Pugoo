class phantom:
    def __init__(self, root, pos, dis, linenum=19):
        self.dim = dis * (linenum - 1)
        self.distance = dis
        self.linenum = linenum
        self.pos = pos
        self.pieces_canvas = [[None for i in range(linenum)] for i in range(linenum)]
        self.create_array()
        self.groups = {}
        self.territory = []
        self.color_pointer = 0

    def show_groups(self, group, show):
       pass

    def show_territory(self, board=None, show=True):
        pass

    def draw_cross(self, axis, ratio=0.2, color='#FFFFFF'):
        pass

    def create_array(self):
       pass

    def drawline(self, num, vertical=False):
        pass

    def create_board(self):
        pass

    def clear(self):
        pass

    def remove_point(self, axis):
        pass

    def add_point(self, point, ratio=0.4):
        pass
