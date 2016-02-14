import sys
from communication import read_map, show_visible
from core import Player, Game

game = Game()
Player(game, 'procrat')
Player(game, 'iasoon')

with open(sys.argv[1], 'r') as handle:
    read_map(game, handle)

game.play()
print(game.winner().name)
