#!/usr/bin/env python
from road import Road
from fort import Fort
from itertools import chain, count, islice, takewhile
import asyncio
from march import *

NO_PLAYER_NAME = 'neutral'

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

def build_road(game, fort1, fort2):
    road = Road(fort1, fort2)
    fort1.roads[fort2] = road
    fort2.roads[fort1] = road
    game.roads.append(road)


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

def parse_command(game, player, string):
    """Returns a Match object if parsing succeeds, else None."""

    try:
        origin, target, size = string.strip().split(' ')
    except ValueError:
        player.warning('A march command should have three parts, got "{}"'
                       .format(string))
        return None
    try:
        origin = game.forts[origin]
    except KeyError:
        player.warning('Couldn\'t find fort "{}"'.format(origin))
        return None
    try:
        target = game.forts[target]
    except KeyError:
        player.warning('Couldn\'t find fort "{}"'.format(target))
        return None
    try:
        size = int(size)
    except ValueError:
        player.warning('"{}" isn\'t a number'.format(size))
        return None
    try:
        road = origin.roads[target]
    except KeyError:
        player.warning('Couldn\'t find road from {} to {}'
                       .format(origin, target))
        return None
    if size < 0:
        player.warning('Can\'t send a negative amount of soldiers.')
        return None
    if origin.owner != player:
        player.warning('Can\'t send soldiers from the fort that is not your '
                       'own.')
        return None

    return March(road, origin, target, player, size)
