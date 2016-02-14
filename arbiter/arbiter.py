#! /usr/bin/python3

from itertools import chain
from collections import defaultdict
from functools import total_ordering
from math import ceil, sqrt
from subprocess import Popen, PIPE
import sys

MARCH_SPEED = 1
NO_PLAYER_NAME = 'neutral'


def read_section(handle):
    header = handle.readline()
    section_length = int(header.split(' ')[0])
    return [handle.readline().rstrip() for i in range(section_length)]


def read_sections(handle, *parsers):
    for parser in parsers:
        for line in read_section(handle):
            parser(line)


def parse_fort(game, string):
    name, x, y, owner, garrison = string.split(' ')
    Fort(game, name, int(x), int(y),
            game.players.get(owner), int(garrison))


def parse_road(game, string):
    a, b = string.split(' ')
    game.forts[a].neighbours.add(game.forts[b])
    game.forts[b].neighbours.add(game.forts[a])


def parse_march(game, string):
    origin, target, owner, size, steps = string.split(' ')
    March(game, game.forts[origin], game.forts[target],
            game.players.get(owner), int(size), int(steps))


def read_map(game, handle):
    read_sections(handle,
            lambda line: parse_fort(game, line),
            lambda line: parse_road(game, line),
            lambda line: parse_march(game, line))


def parse_command(game, player, string):
    origin, target, size = string.split(' ')
    if game.forts[origin] and game.forts[origin].owner == player:
        game.forts[origin].dispatch(game.forts[target], int(size))


def read_commands(game, player, handle):
    read_sections(handle, lambda line: parse_command(game, player, line))


def show_player(player):
    if player:
        return player.name
    return NO_PLAYER_NAME


def show_section(items, name, formatter):
    header = "{} {}:".format(len(items), name)
    body = (formatter(item) for item in items)
    return '\n'.join([header, *body])


def show_fort(fort):
    return "{} {} {} {} {}".format(
            fort.name, fort.x, fort.y, show_player(fort.owner), fort.garrison)


def show_road(road):
    return "{} {}".format(*road)


def show_march(march):
    return "{} {} {} {} {}".format(
            march.origin, march.target, show_player(march.owner),
            march.size, ceil(march.remaining_steps))


def show_visible(game, forts):
    visible_forts = set.union(*(fort.neighbours for fort in forts))
    roads = set(unorder((fort, n)) for fort in forts for n in fort.neighbours)
    marches = list(chain(*(game.roads[road].marches() for road in roads)))
    return '\n'.join([
        show_section(visible_forts, 'forts', show_fort),
        show_section(roads, 'roads', show_road),
        show_section(marches, 'marches', show_march)
        ])


def unorder(tup):
    return tuple(sorted(tup))


class UnorderedTupleDefaultDict(dict):
    def __init__(self, factory):
        self.factory = factory

    def __missing__(self, key):
        self[key] = self.factory(key)
        return self[key]

    def __getitem__(self, key):
        return super().__getitem__(unorder(key))

    def __setitem__(self, key, value):
        return super().__setitem__(unorder(key), value)

@total_ordering
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
        if self.owner:
            self.garrison += 1

    def distance(self, neighbour):
        """ returns distance in steps """
        dist = sqrt((self.x - neighbour.x) ** 2 + (self.y - neighbour.y) ** 2)
        return ceil(dist/MARCH_SPEED)

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return self.name.__hash__()


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



class March:
    def __init__(self, game, origin, target, owner, size, steps):
        self.game = game
        self.origin = origin
        self.target = target
        self.owner = owner
        self.size = size
        self.remaining_steps = steps
        self.road().add(self)
        self.owner.marches.add(self)

    def remove(self):
        self.road().remove(self)
        self.owner.marches.remove(self)

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


class Player:
    def __init__(self, game, name, cmd):
        self.game = game
        self.name = name
        self.forts = set()
        self.marches = set()
        game.players[name] = self
        self.process = Popen(cmd, stdin=PIPE, stdout=PIPE,
                           universal_newlines=True)

    def capture(self, fort):
        if fort.owner:
            fort.owner.forts.remove(fort)
        self.forts.add(fort)
        fort.owner = self

    def is_defeated(self):
        return (not self.forts) and (not self.marches)

    def send_state(self):
        self.process.stdin.write(show_visible(self.game, self.forts))
        self.process.stdin.write('\n')
        self.process.stdin.flush()

    def read_commands(self):
        read_commands(self.game, self, self.process.stdout)




class Game:
    def __init__(self):
        self.forts = {}
        self.players = {}
        self.roads = UnorderedTupleDefaultDict(Road)

    def play(self):
        while not self.winner():
            self.get_commands()
            self.step()
            self.remove_losers()

    def winner(self):
        if len(self.players) > 1:
            return None
        for player in self.players.values():
            return player

    def remove_losers(self):
        for player in list(self.players.values()):
            if player.is_defeated():
                del self.players[player.name]

    def get_commands(self):
        for player in self.players.values():
            player.send_state()
        for player in self.players.values():
            player.read_commands()


    def step(self):
        for road in self.roads.values():
            road.step()
        for fort in self.forts.values():
            fort.step()

game = Game()
Player(game, 'procrat', ['./procrat', 'test2'])
Player(game, 'iasoon', ['./procrat', 'test1'])

with open(sys.argv[1], 'r') as handle:
    read_map(game, handle)

game.play()
print(game.winner().name)
