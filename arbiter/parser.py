import sys
from arbiter import *

class Parser:
    def __init__(self, path):
        self.game = Game()
        self.path = path

    def parse_fort(self, string):
        name, x, y, owner, garrison = string.rstrip().split(' ')
        Fort(self.game, name, float(x), float(y), owner, int(garrison))

    def parse_road(self, string):
        a, b = string.rstrip().split(' ')
        self.game.forts[a].build_road(self.game.forts[b])

    def read_map(self):
        with open(self.path, 'r') as f:
            lines = f.readlines()
        lines = self.process_section(self.parse_fort, lines)
        lines = self.process_section(self.parse_road, lines)

    def process_section(self, fun, lines):
        section_length = int(lines[0].split(' ')[0])
        rest = lines[section_length+1:]
        for line in lines[1:section_length+1]:
            fun(line)
        return rest

    def next_section(self, lines):
        return (section, lines)

    def parse(self):
        self.read_map()
        return self.game
