from itertools import chain, takewhile
from collections import defaultdict

MARCH_SPEED = 1

class Game:
    def __init__(self):
        self.forts = {}
        self.march_dict = UnorderedTupleDict(lambda x: [])

class Fort:
    def __init__(self, game, name, x, y):
        self.game = game
        self.name = name
        self.x = x
        self.y = y
        self.neighbours = Set()
        self.owner = None
        self.garrison = 0
        self.forts[self.name] = self

    def distance(self, neighbour):
        """ returns distance in steps """
        dist = math.sqrt((self.x - neighbour.x) ** 2 + (self.y - neighbour.y) ** 2)
        return math.ceil(dist/MARCH_SPEED)


class March:
    def __init__(self, game, origin, target, size):
        self.game = game
        self.origin = origin
        self.target = target
        self.size = size
        self.remaining_steps = origin.distance(target)


class UnorderedTupleDict(defaultdict):

    def unorder(self, key):
        return tuple(sorted(key))

    def __getitem__(self, key):
        return super().__getitem__(self.unorder(key))

    def __setitem__(self, key, value):
        return super().__setitem__(self.unorder(key), value)

