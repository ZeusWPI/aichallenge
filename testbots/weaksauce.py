from math import ceil, floor, sqrt
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

        self.incoming = {}  # {name: origin(Fort)}
        self.outgoing = {}  # {name: destination(Fort)}
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
        self.origin.outgoing[destination] = self.destination
        self.destination.incoming[origin] = self.origin


class Game:
    players = {}  # {name: player(Player)}
    forts = {}  # {name: fort(Fort)}
    marches = set()  # (march(March))

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
        if owner_name not in Game.players.keys():
            Game.players[owner_name] = Player(owner_name)

        Game.marches.add(March(*line))

    @staticmethod
    def start():
        mind = Mind(ME)

        def handle(handler):
            for i in range(int(input().split()[0])):
                handler(input().split())

        while True:
            Game.players, Game.marches = {}, {}
            handle(Game.parse_fort)
            handle(Game.parse_road)
            handle(Game.parse_march)
            mind.play()
            print(mind.orders())


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
        self.marches = {}  # {destination(Fort): march(March)}
        self.forts = {}  # {name: fort(Fort)}
        self.territory = {}  # {fort(Fort): False|True}
        self.under_attack = {}  # {fort(Fort): False|True}
        self.targets = {}  # {enemy: set(mine)}

    def play(self):
        self.__collect_data()
        self.__defend_borders()
        self.__attack()
        # TODO

    def orders(self):
        return "{} marches:\n".format(len(self.orders())) + \
               '\n'.join(str(command) for command in self.commands)

    def __collect_data(self):
        self.player = Game.players[self.name]
        self.forts = self.player.forts
        self.marches = self.player.marches
        self.territory = {f for f in self.forts if self.__in_safety(f)}
        self.borders = {f for f in self.forts if not self.__in_safety(f)}
        self.under_attack = {f for f in self.forts if self.__threatened(f)}

        self.targets = {}
        for mine in self.forts:
            for tar in mine.neighbours:
                if tar.owner is not self.player:
                    self.targets.update((tar, self.targets[tar] | set(mine)))

    def __attack(self):
        def pressure(f, t):
            return f.garrison / 2 - t.garrison - f.distance(t)

        _max = (5, None)
        for target, prongs in self.targets.values():
            diff = sum(pressure(fort, target) for fort in prongs)
            if diff > _max[0]:
                _max = (diff, target)

        if _max[1] is not None:
            target = _max[1]
            for prong in self.targets[target]:
                self.__apply_command(prong, target, prong.garrison / 2)

    def __defend_borders(self):
        for safe_fort in (f for f, safe in self.territory.items() if safe):
            half = floor(safe_fort.garrison / 2)
            amount = floor(half / len(safe_fort.neighbours))
            for neighbour in safe_fort.neighbours.values():
                self.__apply_command(safe_fort, neighbour, amount)

    def __apply_command(self, origin, destination, amount):
        self.forts[origin].garrison -= amount
        self.commands.add(Command(origin, destination, amount))

    def __in_safety(self, my_fort):
        return all(n.owner == self.player for n in my_fort.neighbours.values())

    def __threatened(self, my_fort):
        return any(e.owner != self.player for e in my_fort.incoming.values())


Game.start()
