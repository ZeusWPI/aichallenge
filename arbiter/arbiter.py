#! /usr/bin/python3

from itertools import chain
from collections import defaultdict
from math import ceil, sqrt
from subprocess import Popen, PIPE
import json
import sys

MARCH_SPEED = 1
NO_PLAYER_NAME = 'neutral'
MAX_STEPS = 25

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
    game.forts[name] = Fort(name, int(x), int(y), game.players.get(owner),
                            int(garrison))


def parse_road(game, string):
    a, b = string.split(' ')
    build_road(game, game.forts[a], game.forts[b])


def parse_march(game, string):
    origin, target, owner, size, steps = string.split(' ')
    origin = game.forts[origin]
    target = game.forts[target]
    owner = game.players[owner]
    origin.roads[target].march(target, owner, int(size), int(steps))


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
    return "{} {}".format(*road.headed_to.keys())


def show_march(tup):
    origin, target, pos, march = tup
    return "{} {} {} {} {}".format(
        origin, target, show_player(march.owner),
        march.size, pos)


def show_visible(forts):
    roads = set(road for fort in forts for road in fort.roads.values())
    forts = set(chain(*(road.headed_to.keys() for road in roads)))
    marches = list(chain(*(road.marches() for road in roads)))
    return '\n'.join([
        show_section(forts, 'forts', show_fort),
        show_section(roads, 'roads', show_road),
        show_section(marches, 'marches', show_march)
    ])


class Road:
    def __init__(self, fort1, fort2):
        self.length = fort1.distance(fort2)
        self.headed_to = {
            fort1: [None] * (self.length * 2 + 1),
            fort2: [None] * (self.length * 2 + 1),
        }

    def march(self, destination, owner, size, steps=None):
        position = 2 * (steps or self.length)
        if self.headed_to[destination][position]:
            self.headed_to[destination][position].size += size
        else:
            march = March(self, owner, size)
            self.headed_to[destination][position] = march

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
        army = lambda ind, fort: self.headed_to[fort][ind]

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


def build_road(game, fort1, fort2):
    road = Road(fort1, fort2)
    fort1.roads[fort2] = road
    fort2.roads[fort1] = road
    game.roads.append(road)


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

    def dispatch(self, neighbour, size):
        road = self.roads.get(neighbour)
        if road:
            size = min(size, self.garrison)
            road.march(neighbour, self.owner, size)
            self.garrison -= size

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
        if self.garrison > 0:
            winner.capture(self)

    def distance(self, neighbour):
        """ returns distance in steps """
        dist = sqrt((self.x - neighbour.x) ** 2 + (self.y - neighbour.y) ** 2)
        return ceil(dist / MARCH_SPEED)

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class March:
    def __init__(self, road, owner, size):
        self.road = road
        self.owner = owner
        self.size = size
        self.owner.marches.add(self)

    def die(self):
        self.owner.marches.remove(self)

    def __repr__(self):
        return str(self.size)


class Player:
    def __init__(self, name, cmd):
        self.name = name
        self.forts = set()
        self.marches = set()
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
        self.process.stdin.write(show_visible(self.forts))
        self.process.stdin.write('\n')
        self.process.stdin.flush()

    def read_commands(self, game):
        read_commands(game, self, self.process.stdout)


class Game:
    def __init__(self, configfile):
        with open(configfile, 'r') as f:
            config = json.load(f)

        self.players = {}
        for name, cmd in config['players'].items():
            self.players[name] = Player(name, cmd)

        self.forts = {}
        self.roads = []
        with open(config['mapfile'], 'r') as f:
            read_map(self, f)

        self.logfile = open(config['logfile'], 'w')

    def play(self):
        steps = 0
        self.logfile.write(show_visible(self.forts.values()))
        self.logfile.write('\n')
        while steps < MAX_STEPS and not self.winner():
            self.get_commands()
            self.step()
            self.remove_losers()
            steps += 1

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
            player.read_commands(self)

    def step(self):
        self.logfile.write(show_visible(self.forts.values()))
        self.logfile.write('\n')
        for road in self.roads:
            road.step()
        for fort in self.forts.values():
            fort.resolve_siege()



game = Game(sys.argv[1])

game.play()
