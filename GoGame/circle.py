class Circle:
    def __init__(self, members, range):
        self.members = members
        self.range = range

    def __str__(self):
        return repr(self.members) + ':' + repr(self.range)


class Circles:
    def __init__(self):
        self.circles = []

    def append(self, other):
        for circle in self.circles:
            if other.members == circle.members:
                return None
        self.circles.append(other)
