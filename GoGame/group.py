class Group():
    def __init__(self, name, members, color):
        self.name = name
        self.members = set(members)
        self.color = color
        self.protected = False
        self.attention = False

    def __str__(self):
        s = ''
        for member in self.members:
            s = s + member.tostring()
        return str(self.name) + ' ' + s + ' ' + str(self.color)