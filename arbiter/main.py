import sys
from parser import *

game = Parser(sys.argv[1]).parse()
for fort in game.forts.values():
    print(fort.name)
    print(list(map(lambda f: f.name, fort.neighbours)))
