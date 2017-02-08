class Group():
    def __init__(self, name, members, color):
        self.name = name
        self.members = set(members)
        self.color = color
        self.protected = False
        self.attention = False
        self.border = False
        self.lines = 0
        self.liberties = []

    def __deepcopy__(self, memodict={}):
        g = Group(self.name, set(tuple(self.members)), self.color)
        g.protected = self.protected
        g.attention = self.attention
        g.border = self.border
        g.lines = self.lines
        g.liberties = self.liberties[:]
        return g

    def combine(self, other):
        if other.color != self.color:
            return None
        self.members = self.members | other.members
        return self

    def extend(self, others):
        if len(others) < 1:
            return None
        group = self.combine(others[0])

    def __str__(self):
        s = ''
        for member in self.members:
            s = s + member.tostring()
        d = dict(name=self.name, color=self.color, life=self.life,
                 lines=self.lines, eyes=self.eyes, size=self.size)
        return repr(d) + s