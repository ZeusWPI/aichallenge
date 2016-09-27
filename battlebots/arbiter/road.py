#!/usr/bin/env python
from math import ceil, sqrt
class Road:
    def __init__(self, fort1, fort2):
        self.length = fort1.distance(fort2)
        self.headed_to = {
            fort1: [None] * (self.length * 2 + 1),
            fort2: [None] * (self.length * 2 + 1),
        }

    def add_march(self, march, steps=None):
        position = 2 * (steps or self.length)
        if self.headed_to[march.destination][position]:
            self.headed_to[march.destination][position].size += march.size
            march.die()
        else:
            self.headed_to[march.destination][position] = march

    def step(self):
        self.half_step()
        self.half_step()

    def half_step(self):
        for marches in self.headed_to.values():
            for i in range(len(marches) - 1):
                marches[i] = marches[i + 1]
            marches[-1] = None
        self.resolve_encounters()

    def resolve_encounters(self):
        def army(ind, fort):
            return self.headed_to[fort][ind]

        fort1, fort2 = self.headed_to.keys()
        for i in range(2 * self.length + 1):
            positions = [(i, fort1), (-i - 1, fort2)]
            armies = [army(*pos) for pos in positions]
            if not all(armies):
                continue
            if len(set(army.owner for army in armies)) == 1:
                continue
            deaths = min(army.size for army in armies)
            for index, fort in positions:
                army(index, fort).size -= deaths
                if army(index, fort).size == 0:
                    army(index, fort).die()
                    self.headed_to[fort][index] = None

    def fetch_arriving(self, fort):
        march = self.headed_to[fort][0]
        self.headed_to[fort][0] = None
        return march

    def marches(self):
        endpoints = list(self.headed_to.keys())
        for destination, origin in [endpoints, reversed(endpoints)]:
            for steps, march in enumerate(self.headed_to[destination]):
                if march:
                    yield (origin, destination, ceil(steps / 2), march)

    def __repr__(self):
        return '<Road {forts}, {length} steps>'.format(
            forts=tuple(self.headed_to.keys()), length=self.length)
