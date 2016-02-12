from itertools import chain, takewhile
from collections import defaultdict

MARCH_SPEED = 1

class Game:
    def __init__(self):
        self.forts = {}
        self.roads = UnorderedTupleDict(lambda x: Road())

class Road:
    def __init__(self):
        self.positions = defaultdict(lambda x: [])

    def add(self, march):
        self.positions[march.pos()].append(march)

    def remove(self, march):
        self.positions[march.pos()].remove(march)

    def marches(self):
        return chain(*self.positions.values())

    def step(self):
        self.half_step()
        self.resolve_encounters()
        self.half_step()
        self.resolve_encounters()

    def half_step(self):
        # the list() call is needed to fixate the current buckets
        for march in list(self.marches()):
            self.remove(march)
            march.remaining_steps -= 0.5
            self.add(march)

    def resolve_encounters(self):
        for bucket in self.positions.values():
            for m1 in bucket:
                for m2 in bucket:
                    m1.encounter(m2)
                    if m1.size <= 0:
                        break


class Fort:
    def __init__(self, game, name, x, y, owner, garrison):
        self.game = game
        self.name = name
        self.x = x
        self.y = y
        self.neighbours = set()
        self.owner = owner
        self.garrison = garrison
        game.forts[name] = self

    def build_road(self, neighbour):
        self.neighbours.add(neighbour)
        neighbour.neighbours.add(self)

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
        self.road().add(self)

    def remove(self):
        self.road().remove(self)

    def kill_soldiers(self, num):
        self.size -= num
        if self.size <= 0:
            self.remove()

    def encounter(self, other):
        if self.owner != other.owner:
            tmp = other.size
            other.kill_soldiers(self.size)
            self.kill_soldiers(tmp)


    def road(self):
        self.game.roads[self.origin, self.target]

    def pos(self):
        if self.origin == min(self.origin, self.target):
            return self.origin.distance(self.target) - self.remaining_steps
        else:
            return self.remaining_steps


class UnorderedTupleDict(defaultdict):

    def unorder(self, key):
        return tuple(sorted(key))

    def __getitem__(self, key):
        return super().__getitem__(self.unorder(key))

    def __setitem__(self, key, value):
        return super().__setitem__(self.unorder(key), value)
