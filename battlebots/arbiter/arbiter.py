#! /usr/bin/python3
import asyncio
import json
from game import Game
from parser import *
import logging

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Let some bots battle.')
    parser.add_argument('config_file', help='a file containing all battle and '
                        'bot configuration in JSON format')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='whether to show debugging info')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    with open(args.config_file, 'r') as config_file:
        config = json.load(config_file)

    with open(config['mapfile'], 'r') as map_file:
        with open(config['logfile'], 'w') as log_file:
            game = Game(config['players'], map_file, config['max_steps'],
                        log_file, run_in_shell=True)
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(game.play_async())
                print('Winner: {}'.format(game.winner()))
            finally:
                loop.close()
