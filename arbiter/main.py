import sys
from parser import *

game = MapParser().parse(sys.argv[1])
CommandParser(game, "bart").parse(sys.argv[2])
for fort in game.forts.values():
    print(fort.name)
    print(list(map(lambda f: f.name, fort.neighbours)))
for k, road in game.roads.items():
    print(k)
    for pos, bucket in road.positions.items():
        print(pos, list(map(lambda m: m.size, bucket)))
