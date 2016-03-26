#! /usr/bin/python3

from itertools import chain, count, islice, takewhile
from collections import defaultdict
from math import ceil, sqrt
import json
import sys
import asyncio
from asyncio import subprocess as sp

MARCH_SPEED = 1
NO_PLAYER_NAME = 'neutral'
BOT_TIMEOUT = 2  # seconds


def read_section(lines):
    line = next(lines)
    while ':' not in line:
        line = next(lines)
    # found a header
    n_lines, _ = line.rstrip(':').split(' ')
    if n_lines == '?':
        return takewhile(lambda line: line.strip() != 'end', lines)
    else:
        return islice(lines, int(n_lines))


def parse_sections(map_file, *parsers):
    # ignore empty lines and lines starting with a #
    lines = (line.rstrip() for line in map_file
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
    road = origin.roads[target]
    owner = game.players[owner]
    march = March(road, origin, target, owner, int(size))
    march.dispatch(int(steps))


def read_map(game, map_file):
    parse_sections(map_file,
                   lambda line: parse_fort(game, line),
                   lambda line: parse_road(game, line),
                   lambda line: parse_march(game, line))


def parse_command(game, player, string):
    try:
        origin, target, size = string.split(' ')
        origin, target = game.forts[origin], game.forts[target]
        size = int(size)
        road = origin.roads[target]
        if road and origin.owner == player and size >= 0:
            return March(road, origin, target, player, size)
    except (KeyError, ValueError):
        # TODO add warning to bot and log warning
        pass

    return None


def show_player(player):
    if player:
        return player.name
    return NO_PLAYER_NAME


def show_section(items, name, formatter):
    header = "{} {}:".format(len(items), name)
    body = (formatter(item) for item in items)
    return '\n'.join([header] + list(body))


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

    def __repr__(self):
        return '<Road {forts}, {length} steps>'.format(
            forts=tuple(self.headed_to.keys()), length=self.length)


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
        return '<Fort {name}>'.format(**self.__dict__)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class March:
    def __init__(self, road, origin, destination, owner, size):
        self.road = road
        self.origin = origin
        self.destination = destination
        self.owner = owner
        self.size = size
        self.owner.marches.add(self)

    def dispatch(self, steps=None):
        if self.size > self.origin.garrison:
            # TODO add warning to bot that it's trying to sent more soldiers
            # than available
            pass
        size = min(self.size, self.origin.garrison)
        self.origin.garrison -= size
        self.road.add_march(self, steps)

    def die(self):
        self.owner.marches.remove(self)

    def __repr__(self):
        return ('<March from {origin} to {destination} by {owner} '
                'with {size} soldiers>'.format(**self.__dict__))


@asyncio.coroutine
def async_read_line(stream):
    """
    Return the next non-empty line or raise an EOFError if at the end of the
    stream.
    """
    while True:
        byteline = yield from stream.readline()
        if not byteline:
            raise EOFError
        line = byteline.decode('utf-8').strip()
        if line and not line.startswith("#"):
            return line


@asyncio.coroutine
def async_slice(coro_iterable, stop):
    xs = []
    for _ in range(stop):
        x = yield from next(coro_iterable)
        xs.append(x)
    return xs


@asyncio.coroutine
def async_takewhile(predicate, coro_iterable):
    xs = []
    while True:
        x = yield from next(coro_iterable)
        if not predicate(x):
            break
        xs.append(x)
    return xs


@asyncio.coroutine
def async_read_section(stream):
    lines = (async_read_line(stream) for _ in count())
    header = yield from next(lines)
    n_lines, _ = header.split(' ')
    if n_lines == '?':
        def not_at_end(line): return line.strip() != 'end'
        section = yield from async_takewhile(not_at_end, lines)
    else:
        section = yield from async_slice(lines, int(n_lines))
    return section


class Player:
    def __init__(self, name, cmd):
        self.name = name
        self.forts = set()
        self.marches = set()
        self.cmd = '{} {}'.format(cmd, name).encode('utf8')
        self.in_control = True

    @asyncio.coroutine
    def start_process(self):
        # TODO save stderr as user feedback
        self.process = yield from asyncio.create_subprocess_shell(
            self.cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

    def stop_process(self):
        self.process.kill()
        self.process._transport.close()

    def capture(self, fort):
        if fort.owner:
            fort.owner.forts.remove(fort)
        fort.owner = self
        self.forts.add(fort)

    def is_defeated(self):
        return (not self.forts) and (not self.marches)

    def remove_control(self):
        self.stop_process()
        sys.stderr.write("Removing control from {}.\n".format(self.name))
        self.in_control = False

    @asyncio.coroutine
    def orders(self, game):
        # Send current state
        state = show_visible(self.forts)
        encoded = (state + '\n').encode('utf-8')
        self.process.stdin.write(encoded)
        yield from self.process.stdin.drain()

        # Read bot's marches
        try:
            coroutine = async_read_section(self.process.stdout)
            section = yield from asyncio.wait_for(coroutine, BOT_TIMEOUT)
            marches = (parse_command(game, self, line) for line in section)
            return marches
        except asyncio.TimeoutError:
            sys.stderr.write('{} timed out!\n'.format(self.name))
            self.remove_control()
            return []
        except EOFError:
            sys.stderr.write('{} stopped writing unexpectedly.\n'
                             .format(self.name))
            self.remove_control()
            return []

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Player {name}>'.format(**self.__dict__)


class Game:
    def __init__(self, playermap, mapfile, max_steps, logfile):
        self.max_steps = max_steps
        self.logfile = logfile

        self.players = {name: Player(name, cmd)
                        for name, cmd in playermap.items()}

        self.forts = {}
        self.roads = []
        # TODO this could work in a better fashion ...
        read_map(self, mapfile)

    def play(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.play_async())
        finally:
            loop.close()

    @asyncio.coroutine
    def play_async(self):
        steps = 0

        for player in self.players.values():
            yield from player.start_process()

        try:
            while steps < self.max_steps and not self.winner():
                self.log(steps)
                yield from self.get_commands()
                self.step()
                self.remove_losers()
                steps += 1
                print('Completed step', steps, file=sys.stderr)
            self.log(steps)

        finally:
            for player in self.players.values():
                player.stop_process()

    def log(self, step):
        self.logfile.writelines(["# STEP: " + str(step) + "\n",
                                 show_visible(self.forts.values()) + "\n",
                                 "\n"])

    def winner(self):
        """
        Returns the player instance of the winner or None in case of a draw.
        """
        if len(self.players) > 1:
            return None
        return next(self.players.values())

    def remove_losers(self):
        for player in list(self.players.values()):
            if player.is_defeated():
                del self.players[player.name]

    @asyncio.coroutine
    def get_commands(self):
        coroutines = (player.orders(self) for player in self.players.values())
        orders = yield from asyncio.gather(*coroutines)
        for march in chain(*orders):
            if march:
                march.dispatch()

    def step(self):
        for road in self.roads:
            road.step()
        for fort in self.forts.values():
            fort.step()


if __name__ == '__main__':
    # TODO use argparser
    assert len(sys.argv) > 1
    config_file = sys.argv[1]

    with open(config_file, 'r') as f:
        config = json.load(f)

    with open(config['mapfile'], 'r') as map_file:
        with open(config['logfile'], 'w') as log_file:
            game = Game(config['players'], map_file, config['max_steps'],
                        log_file)
            game.play()
            print('Winner: {}'.format(game.winner()))
