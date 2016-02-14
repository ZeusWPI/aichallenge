import sys
from itertools import chain
from math import ceil

from core import Game, Fort, March, unorder


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
    Fort(game, name, float(x), float(y),
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
        origin.dispatch(game.forts[target], int(size))


def read_commands(game, player, handle):
    read_sections(handle, lambda line: parse_command(game, player, line))


def show_player(player):
    if player:
        return player.name
    return NO_PLAYER_NAME


def show_section(items, name, fun):
    header = "{} {}:".format(len(items), name)
    body = (fun(item) for item in items)
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
