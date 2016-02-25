from math import ceil, sqrt
import sys

MARCH_SPEED = 1
ME = sys.argv[1]


class Player:
    def __init__(self, name):
        self.name = name
        self.marches = set()
        self.forts = {}  # {name: fort(Fort)}


class Fort:
    def __init__(self, name, x, y, owner, garrison):
        self.name = name
        self.x = int(x)
        self.y = int(y)
        self.neighbours = {}  # {name: fort(Fort)}
        self.owner = Game.players[owner]
        self.garrison = int(garrison)

        self.incoming_marches = {}  # {name: origin(Fort)}
        self.outgoing_marches = {}  # {name: destination(Fort)}
        Game.players[owner].forts[name] = self

    def distance(self, neighbour):
        """ returns distance in steps"""
        dist = sqrt((self.x - neighbour.x) ** 2 + (self.y - neighbour.y) ** 2)
        return ceil(dist / MARCH_SPEED)

    def update(self, name, x, y, owner, garrison):
        self.name = name
        self.x = int(x)
        self.y = int(y)
        self.garrison = int(garrison)
        self.owner = Game.players[owner]
        Game.players[owner].forts[name] = self

    def add_neighbour(self, neighbour):
        self.neighbours[neighbour.name] = self.distance(neighbour)


class March:
    def __init__(self, origin, destination, owner, size, remaining_steps):
            self.origin = Game.forts[origin]
            self.destination = Game.forts[destination]
            self.owner = Game.players[owner]
            self.size = size
            self.remaining_steps = remaining_steps

            self.owner.marches.add(self)
            self.origin.outgoing_marches[destination] = self.destination
            self.destination.incoming_marches[origin] = self.origin


class Game:
    players = {}  # {name: player(Player)}
    forts = {}    # {name: fort(Fort)}
    marches = {}  # {origin: march(March)}

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
        origin = line[0]
        owner_name = line[2]
        if owner_name not in Game.players.keys():
            Game.players[owner_name] = Player(owner_name)

        Game.marches[origin] = March(*line)

    @staticmethod
    def start():
        def handle(handler):
            for i in range(int(input().split()[0])):
                handler(input().split())

        while True:
            Game.players, Game.marches = {}, {}
            handle(Game.parse_fort)
            handle(Game.parse_road)
            handle(Game.parse_march)
            print("Turn read")


Game.start()

