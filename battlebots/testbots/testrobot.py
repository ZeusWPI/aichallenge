#! /usr/bin/python3

from math import ceil, sqrt
from collections import defaultdict
import sys

MARCH_SPEED = 1
ME = sys.argv[1]


class Player:
    def __init__(self, name):
        self.name = name
        self.marches = set()
        self.forts = set()


class Fort:
    def __init__(self, name, x, y, owner, garrison):
        self.name = name
        self.x = int(x)
        self.y = int(y)
        self.garrison = int(garrison)
        self.owner = Game.players[owner]

        self.neighbours = set()
        self.incoming = {}
        self.outgoing = {}
        Game.players[owner].forts.add(self)

    def distance(self, neighbour):
        """ returns distance in steps"""
        dist = sqrt((self.x - neighbour.x) ** 2 + (self.y - neighbour.y) ** 2)
        return ceil(dist / MARCH_SPEED)

    def update(self, name, x, y, owner, garrison):
        self.incoming = {}
        self.outgoing = {}
        self.name = name
        self.x = int(x)
        self.y = int(y)
        self.garrison = int(garrison)
        self.owner = Game.players[owner]
        Game.players[owner].forts.add(self)

    def add_neighbour(self, neighbour):
        self.neighbours.add(neighbour)


class March:
    def __init__(self, origin, destination, owner, size, remaining_steps):
        self.origin = Game.forts[origin]
        self.destination = Game.forts[destination]
        self.owner = Game.players[owner]
        self.size = size
        self.remaining_steps = remaining_steps

        self.owner.marches.add(self)
        self.origin.outgoing[destination] = self.destination
        self.destination.incoming[origin] = self.origin


class Game:
    forts = {}  # {name: fort(Fort)}
    players = {}  #
    marches = set()

    @staticmethod
    def parse_fort(line):
        fort_name = line[0]
        owner_name = line[3]
        Game.players[owner_name] = Player(owner_name)

        if fort_name in Game.forts.keys():
            Game.forts[fort_name].update(*line)
        else:
            Game.forts[fort_name] = Fort(*line)

    @staticmethod
    def parse_road(line):
        Game.forts[line[0]].add_neighbour(Game.forts[line[1]])
        Game.forts[line[1]].add_neighbour(Game.forts[line[0]])

    @staticmethod
    def parse_march(line):
        owner_name = line[2]
        if owner_name not in Game.players:
            Game.players[owner_name] = Player(owner_name)

        Game.marches.add(March(*line))

    @staticmethod
    def start():
        mind = Mind(ME)

        def handle(handler):
            for i in range(int(input().split()[0])):
                handler(input().split())

        try:
            while True:
                Game.players, Game.marches = {}, set()
                handle(Game.parse_fort)
                handle(Game.parse_road)
                handle(Game.parse_march)
                mind.play()
                print(mind.orders())
        except EOFError:
            pass


class Command:
    def __init__(self, origin, destination, garrison):
        self.origin = origin
        self.destination = destination
        self.garrison = garrison

    def __str__(self):
        return "{} {} {}".format(
            self.origin.name,
            self.destination.name,
            self.garrison
        )


class Mind:
    def __init__(self, name):
        self.name = name
        self.player = None
        self.turn = 0
        self.commands = set()
        self.forts = set()
        self.territory = set()
        self.borders = set()
        self.neutral = set()
        self.under_attack = set()
        self.marches = {}
        self.targets = defaultdict(set)

    def play(self):
        self.__collect_data()
        self.__get_neutral()
        self.__defend_borders()
        self.__attack()
        # TODO

    def orders(self) -> str:
        amount = "{} marches:".format(len(self.commands))
        commands = [str(command) for command in self.commands]
        return '\n'.join([amount] + commands)

    def __collect_data(self):
        self.player = Game.players[self.name]
        self.forts = self.player.forts
        self.marches = self.player.marches
        self.territory = set(f for f in self.forts if self.__in_safety(f))
        self.borders = set(f for f in self.forts if not self.__in_safety(f))
        self.neutral = set(f for f in Game.forts.values() if f.owner == 'neutral')
        self.under_attack = set(f for f in self.forts if self.__threatened(f))

        self.targets = defaultdict(set)
        for mine in self.forts:
            for tar in mine.neighbours:
                if tar.owner is not self.player:
                    tmp = self.targets[tar].union([mine])
                    self.targets.update([(tar, tmp)])

    def __get_neutral(self):
        for fort in self.borders:
            neuts = self.neutral.intersection(fort.neighbours)
            for neut in neuts:
                if neut.garrison <= fort.garrison:
                    self.__apply_command(fort, neut, neut.garrison)

    def __attack(self):
        def pressure(f, t):
            return f.garrison // 2 - t.garrison - f.distance(t)

        _max = (1, None)
        for target, prongs in self.targets.items():
            diff = sum(pressure(fort, target) for fort in prongs)
            if diff > _max[0]:
                _max = (diff, target)

        if _max[1] is not None:
            target = _max[1]
            for prong in self.targets[target]:
                self.__apply_command(prong, target, prong.garrison // 2)

    def __defend_borders(self):
        for safe_fort in self.territory:
            half = safe_fort.garrison // 2
            targets = safe_fort.neighbours.difference(self.territory)
            amount = half // len(targets)
            for neighbour in targets:
                self.__apply_command(safe_fort, neighbour, amount)

    def __apply_command(self, origin, destination, amount):
        origin.garrison -= amount
        self.commands.add(Command(origin, destination, amount))

    def __in_safety(self, my_fort):
        return all(n.owner not in (self.player, Game.players.get('neutral'))
                   for n in my_fort.neighbours)

    def __threatened(self, my_fort):
        return any(t.owner is my_fort.owner for t in my_fort.incoming.values())


Game.start()
