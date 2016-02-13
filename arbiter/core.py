from itertools import chain
from collections import defaultdict
import functools
import math


MARCH_SPEED = 1
NO_PLAYER_NAME = 'neutral'


class Game:
    def __init__(self):
        self.forts = {}
        self.players = DefaultDict(lambda name: Player(self, name))
        self.roads = UnorderedTupleDefaultDict(Road)

    def step(self):
        for road in self.roads.values():
            road.step()
        for fort in self.forts.values():
            fort.step()


class Player:
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.forts = set()
        game.players[name] = self

    def capture(self, fort):
        if fort.owner:
            fort.owner.surrender(fort)
        self.forts.add(fort)
        fort.owner = self

    def surrender(self, fort):
        self.forts.remove(fort)


class Road:
    def __init__(self, ends):
        self.positions = defaultdict(lambda: [])
        self.start, self.end = ends
        self.length = self.start.distance(self.end)

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
        self.resolve_arrivals()

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

    def resolve_arrivals(self):
        for march in chain(self.positions[0], self.positions[self.length]):
            march.arrive()


@functools.total_ordering
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
        if owner:
            owner.forts.add(self)

    def dispatch(self, neighbour, size):
        if neighbour in self.neighbours:
            size = min(size, self.garrison)
            steps = self.distance(neighbour)
            March(self.game, self, neighbour, self.owner, size, steps)
            self.garrison -= size

    def reinforce(self, march):
        if self.garrison < 0:
            self.garrison = 0
        self.garrison += march.size
        march.remove()

    def besiege(self, march):
        tmp = self.garrison
        self.garrison -= march.size
        march.kill_soldiers(tmp)
        if self.garrison < 0:
            march.owner.capture(self)
            self.reinforce(march)

    def step(self):
        self.garrison += 1

    def distance(self, neighbour):
        """ returns distance in steps """
        dist = math.sqrt((self.x - neighbour.x) ** 2 + (self.y - neighbour.y) ** 2)
        return math.ceil(dist/MARCH_SPEED)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return self.name.__hash__()


class March:
    def __init__(self, game, origin, target, owner, size, steps):
        self.game = game
        self.origin = origin
        self.target = target
        self.owner = owner
        self.size = size
        self.remaining_steps = steps
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

    def arrive(self):
        if self.owner == self.target.owner:
            self.target.reinforce(self)
        else:
            self.target.besiege(self)

    def road(self):
        return self.game.roads[self.origin, self.target]

    def pos(self):
        if self.origin == min(self.origin, self.target):
            return self.road().length - self.remaining_steps
        else:
            return self.remaining_steps

def unorder(tup):
    return tuple(sorted(tup))


class DefaultDict(dict):
    def __init__(self, factory):
        self.factory = factory

    def __missing__(self, key):
        self[key] = self.factory(key)
        return self[key]


class UnorderedTupleDefaultDict(DefaultDict):
    def __getitem__(self, key):
        return super().__getitem__(unorder(key))

    def __setitem__(self, key, value):
        return super().__setitem__(unorder(key), value)
