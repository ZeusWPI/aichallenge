#! /usr/bin/python3

from itertools import chain, islice
from collections import defaultdict
from math import ceil, sqrt
import json
import sys

import asyncio
from asyncio import subprocess

MARCH_SPEED = 1
NO_PLAYER_NAME = 'neutral'
BOT_TIMEOUT = 2  # seconds


def read_section(iterable):
    header = next(iterable)
    section_length = int(header.split(' ')[0])
    return islice(iterable, section_length)


def read_sections(lines, *parsers):
    # ignore empty lines and lines starting with a #
    lines = (line.rstrip() for line in lines
             if len(line.rstrip()) > 0 and not line.startswith("#"))
    for parser in parsers:
        for line in read_section(lines):
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
    March(origin.roads[target], target, owner, int(size)).dispatch(int(steps))


def read_map(game, handle):
    read_sections(handle,
                  lambda line: parse_fort(game, line),
                  lambda line: parse_road(game, line),
                  lambda line: parse_march(game, line))


def parse_command(game, player, string):
    try:
        origin, target, size = string.split(' ')
        if not (origin in game.forts and target in game.forts):
            return None
        road = game.forts[origin].roads[game.forts[target]]
        if road and game.forts[origin].owner == player:
            return March(road, player, int(size))
    except ValueError:
        return None


def show_player(player):
    if player:
        return player.name
    return NO_PLAYER_NAME


def show_section(items, name, formatter):
    header = "{} {}:".format(str(len(items)), name)
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

    def add_march(self, march, steps=None):
        position = 2 * (steps or self.length)
        if self.headed_to[march.destination][position]:
            self.headed_to[march.destination][position].size += march.size
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
        size = min(size, self.garrison)
        if road and size > 0:
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
    def __init__(self, road, destination, owner, size):
        self.road = road
        self.destination = destination
        self.owner = owner
        self.size = size
        self.owner.marches.add(self)

    def dispatch(self, steps=None):
        self.road.add_march(self, steps)

    def die(self):
        self.owner.marches.remove(self)


@asyncio.coroutine
def async_read_line(stream):
    byteline = yield from stream.readline()
    line = byteline.decode('utf-8').rstrip()
    if not line:
        raise EOFError
    return line


@asyncio.coroutine
def async_read_section(stream):
    header = yield from async_read_line(stream)
    num_lines = int(header.split(' ')[0])
    section = []
    for _ in range(num_lines):
        line = yield from async_read_line(stream)
        section.append(line)
    return section


class Player:
    def __init__(self, name, cmd):
        self.name = name
        self.forts = set()
        self.marches = set()
        self.in_control = True
        self.cmd = cmd

    @asyncio.coroutine
    def start_process(self):
        self.process = yield from asyncio.create_subprocess_exec(
                *self.cmd.split(' '),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
                )

    def capture(self, fort):
        if fort.owner:
            fort.owner.forts.remove(fort)
        fort.owner = self
        self.forts.add(fort)

    def is_defeated(self):
        return (not self.forts) and (not self.marches)

    def remove_control(self):
        self.process.kill()
        sys.stderr.write("Removing control from {}.\n".format(self.name))
        self.in_control = False

    @asyncio.coroutine
    def orders(self, game):
        state = show_visible(self.forts)
        encoded = (state + '\n').encode('utf-8')
        self.process.stdin.write(encoded)
        self.process.stdin.drain()
        try:
            coroutine = async_read_section(self.process.stdout)
            section = yield from asyncio.wait_for(coroutine, BOT_TIMEOUT)
            marches = (parse_command(game, self, line) for line in section)
            return marches
        except asyncio.TimeoutError:
            sys.stderr.write("{} timed out!\n".format(self.name))
            self.remove_control()
            return []
        except EOFError:
            # TODO: how should this be handled?
            return []


class Game:
    def __init__(self, configfile):
        with open(configfile, 'r') as f:
            config = json.load(f)
        self.maxsteps = config['max_steps']
        self.players = {}
        for name, cmd in config['players'].items():
            self.players[name] = Player(name, cmd)

        self.forts = {}
        self.roads = []
        with open(config['mapfile'], 'r') as f:
            read_map(self, f)

        self.logfile = open(config['logfile'], 'w')

    @asyncio.coroutine
    def play(self):
        steps = 0

        for player in self.players.values():
            yield from player.start_process()

        while steps < self.maxsteps and not self.winner():
            print(steps)
            self.log(steps)
            yield from self.get_commands()
            self.step()
            self.remove_losers()
            steps += 1
        self.log(steps)

    def log(self, step):
        self.logfile.writelines(["# STEP: " + str(step) + "\n",
                                 show_visible(self.forts.values()) + "\n",
                                 "\n"])

    def winner(self):
        if len(self.players) > 1:
            return None
        for player in self.players.values():
            return player

    def remove_losers(self):
        for player in list(self.players.values()):
            if player.is_defeated():
                del self.players[player.name]

    @asyncio.coroutine
    def get_commands(self):
        coroutines = (player.orders(self) for player in self.players.values())
        orders = yield from asyncio.gather(*coroutines)

    def step(self):
        for road in self.roads:
            road.step()
        for fort in self.forts.values():
            fort.step()


game = Game(sys.argv[1])

loop = asyncio.get_event_loop()
loop.run_until_complete(game.play())
loop.close()
