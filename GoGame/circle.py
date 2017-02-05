class Circle:
    def __init__(self, members, encloesd, color, key, range=None, type='normal'):  # type = 'normal', 'internal', 'dual'
        self.members = set(members)
        self.enclosed = set(encloesd)
        self.color = color
        self.range = range
        self.type = type
        self.key = key

    def __str__(self):
        return 'Members:' + repr(self.members) + '\n' + repr(self.range) + '\nEnclosed:' + repr(self.enclosed)

    def __repr__(self):
        return self.__str__()


class Circles:
    def __init__(self):
        self.circles = {}

    def append(self, other):
        if other.key in self.circles:
            return None
        else:
            self.circles[other.key] = other

    def extend(self, other):
        for key in other.circles:
            self.append(other.circles[key])

    def __str__(self):
        res = ''
        for circle in self.circles:
            res += repr(circle) + '\n'
        return res

    def __repr__(self):
        return self.__str__()