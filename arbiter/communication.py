import sys
from arbiter import Game, Fort, March
from itertools import chain

class Parser:
    def process_section(self, fun, lines):
        section_length = int(lines[0].split(' ')[0])
        rest = lines[section_length+1:]
        for line in lines[1:section_length+1]:
            fun(line)
        return rest

    def parse(self, path):
        with open(path, 'r') as f:
            lines = f.readlines()
        return self.process(lines)


class MapParser(Parser):
    def __init__(self):
        self.game = Game()

    def parse_fort(self, string):
        name, x, y, owner, garrison = string.rstrip().split(' ')
        Fort(self.game, name, float(x), float(y), owner, int(garrison))

    def parse_road(self, string):
        a, b = string.rstrip().split(' ')
        self.game.forts[a].build_road(self.game.forts[b])

    def parse_march(self, string):
        origin, target, owner, size, steps = string.rstrip().split(' ')
        March(self.game, self.game.forts[origin], self.game.forts[target],
              owner, int(size), int(steps))

    def read_map(self, lines):
        lines = self.process_section(self.parse_fort, lines)
        lines = self.process_section(self.parse_road, lines)
        self.process_section(self.parse_march, lines)

    def process(self, lines):
        self.read_map(lines)
        return self.game

class CommandParser(Parser):
    def __init__(self, game, player):
        self.game = game
        self.player = player

    def parse_command(self, string):
        origin, target, size = string.rstrip().split(' ')
        origin, target = self.game.forts[origin], self.game.forts[target]
        if origin and origin.owner == self.player:
            origin.dispatch(target, int(size))

    def process(self, lines):
        self.process_section(self.parse_command, lines)

def show_section(items, name, fun):
    header = "{} {}:".format(len(items), name)
    body = (fun(item) for item in items)
    return '\n'.join([header, *body])

def show_fort(fort):
    return "{} {} {} {} {}".format(
            fort.name, fort.x, fort.y, fort.owner, fort.garrison)

def show_road(road):
    return "{} {}".format(*road)

def show_march(march):
    return "{} {} {} {} {}".format(
            march.origin, march.target, march.owner,
            march.size, march.remaining_steps)

def show_visible(game, forts):
    visible_forts = set.union(*(fort.neighbours for fort in forts))
    roads = set.union(*(fort.roads() for fort in forts))
    marches = list(chain(*(game.roads[road].marches() for road in roads)))
    return '\n'.join([
        show_section(visible_forts, 'forts', show_fort),
        show_section(roads, 'roads', show_road),
        show_section(marches, 'marches', show_march)
        ])
