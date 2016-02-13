import sys
from communication import *
from arbiter import *

with open(sys.argv[1], 'r') as handle:
    game = read_game(handle)

print(show_visible(game, game.forts.values()))
