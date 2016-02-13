import sys
from communication import read_game, show_visible

with open(sys.argv[1], 'r') as handle:
    game = read_game(handle)

for i in range(4):
    print(show_visible(game, game.forts.values()))
    print('\n')
    game.step()
