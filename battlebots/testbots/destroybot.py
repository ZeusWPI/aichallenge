#! /usr/bin/python3

import sys


class Fort:
    def __init__(self, name, xpos, ypos, owner, armies):
        self.name = name
        self.xpos = xpos
        self.ypos = ypos
        self.owner = owner
        self.armies = armies
        self.neighbours = set()


class March:
    def __init__(self, origin, destination, owner, size, steps_left):
        self.size = size
        self.origin = origin
        self.owner = owner
        self.destination = destination
        self.steps_left = steps_left


class Game:
    def __init__(self, name):
        self.name = name
        self.fortdict = dict()
        self.own_forts = set()
        self.enemy_forts = set()
        self.neutral_forts = set()
        self.own_marches = set()
        self.enemy_marches = set()
        self.parse_input()

    def parse_input(self):
        self.parse_forts()
        self.parse_roads()
        self.parse_marches()

    def parse_forts(self):
        for i in range(int(input().split()[0])):
            line = input().split()
            fort = Fort(line[0], int(line[1]), int(line[2]), line[3], int(line[4]))
            self.fortdict[fort.name] = fort
            if fort.owner == self.name:
                self.own_forts.add(fort)
            elif fort.owner == "neutral":
                self.neutral_forts.add(fort)
            else:
                self.enemy_forts.add(fort)

    def parse_roads(self):
        for i in range(int(input().split()[0])):
            line = input().split()
            fort1 = self.fortdict[line[0]]
            fort2 = self.fortdict[line[1]]
            fort1.neighbours.add(fort2)
            fort2.neighbours.add(fort1)

    def parse_marches(self):
        for i in range(int(input().split()[0])):
            line = input().split()
            march = March(self.fortdict[line[0]], self.fortdict[line[1]], line[2], int(line[3]), int(line[4]))
            if march.owner == self.name:
                self.own_marches.add(march)
            else:
                self.enemy_marches.add(march)

    def play(self):
        commands = []
        for fort in self.own_forts:
            size = fort.armies - 5
            each = size//len(fort.neighbours)
            for neighbour in fort.neighbours:
                commands.append("{} {} {}".format(fort.name, neighbour.name, each))
        print("{} marches:".format(len(commands)))
        for command in commands:
            print(command)


try:
    while True:
        game = Game(sys.argv[1])
        game.play()
except EOFError:
    pass
