import sys
from communication import read_game, show_visible

with open(sys.argv[1], 'r') as handle:
    game = read_game(handle)

game.play()
print(game.winner().name)
