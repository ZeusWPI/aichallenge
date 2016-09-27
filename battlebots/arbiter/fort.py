#!/usr/bin/env python
from math import ceil, sqrt
from collections import defaultdict
MARCH_SPEED = 1
class Fort:
    def __init__(self, name, x, y, owner, garrison):
        self.name = name
        self.x = x
        self.y = y
        self.roads = {}
        self.owner = owner
        self.garrison = garrison
        if owner:
            owner.forts.add(self)

    def step(self):
        self.resolve_siege()
        if self.owner:
            self.garrison += 1

    def fetch_armies(self):
        forces = defaultdict(lambda: 0)
        forces[self.owner] = self.garrison
        for road in self.roads.values():
            march = road.fetch_arriving(self)
            if march:
                forces[march.owner] += march.size
                march.die()
        return forces

    def resolve_siege(self):
        forces = self.fetch_armies()

        def largest_force():
            return max(forces.keys(), key=lambda k: forces[k])
        winner = largest_force()
        self.garrison = forces[winner]
        del forces[winner]
        if forces:
            runner_up = largest_force()
            self.garrison -= forces[runner_up]
        if self.garrison > 0 and winner:
            winner.capture(self)

    def distance(self, neighbour):
        """ returns distance in steps """
        dist = sqrt((self.x - neighbour.x) ** 2 + (self.y - neighbour.y) ** 2)
        return ceil(dist / MARCH_SPEED)

    def __repr__(self):
        return '<Fort {name}>'.format(**self.__dict__)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
