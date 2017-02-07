class Group():
    def __init__(self, name, members, color):
        self.name = name
        self.members = set(members)
        self.color = color
        self.protected = False
        self.attention = False
        self.border = False
        self.lines = 0
        self.liberties = set()
        self.eyes = -1
        self.size = -1
        self.life = -1

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
                 lines=self.lines, eyes=self.eyes, size=self.size, liberties=self.liberties)
        return repr(d) + s