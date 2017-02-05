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

    def combine(self, other):
        if other.color != self.color:
            return None
        group = Group(self.name, self.members | other.members, self.color)
        return group

    def __str__(self):
        s = ''
        for member in self.members:
            s = s + member.tostring()
        return str(self.name) + ' ' + s + ' ' + str(self.color)