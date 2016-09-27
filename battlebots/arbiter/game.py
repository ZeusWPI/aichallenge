#!/usr/bin/env python
import asyncio
from parser import *
from player import *
class Game:
    def __init__(self, playermap, mapfile, max_steps, logfile,
                 run_in_shell=False):
        self.max_steps = max_steps
        self.logfile = logfile

        self.players = {name: Player(name, cmd, run_in_shell)
                        for name, cmd in playermap.items()}

        self.forts = {}
        self.roads = []
        # TODO this could work in a better fashion ...
        read_map(self, mapfile)

    @asyncio.coroutine
    def play_async(self):
        steps = 0

        for player in self.players.values():
            yield from player.start_process()

        try:
            while steps < self.max_steps and len(self.players) > 1:
                self.log(steps)
                yield from self.get_commands()
                self.step()
                yield from self.remove_losers()
                steps += 1
                logging.info('Completed step {}'.format(steps))
            self.log(steps)

        finally:
            for player in self.players.values():
                yield from player.stop_process()

    def log(self, step):
        self.logfile.writelines(["# STEP: " + str(step) + "\n",
                                 show_visible(self.forts.values()) + "\n",
                                 "\n"])

    def winner(self):
        """
        Returns the player instance of the winner or None in case of a draw.
        """
        if len(self.players) != 1:
            return None
        return next(iter(self.players.values()))

    @asyncio.coroutine
    def remove_losers(self):
        for player in list(self.players.values()):
            if player.is_defeated():
                yield from player.stop_process()
                del self.players[player.name]

    @asyncio.coroutine
    def get_commands(self):
        coroutines = (player.orders(self) for player in self.players.values())
        orders = yield from asyncio.gather(*coroutines)
        for march in chain(*orders):
            if march:
                march.dispatch()

    def step(self):
        for road in self.roads:
            road.step()
        for fort in self.forts.values():
            fort.step()
