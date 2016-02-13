import sys
from communication import *
from arbiter import *

game = MapParser().parse(sys.argv[1])
print(show_visible(game, game.forts.values()))
