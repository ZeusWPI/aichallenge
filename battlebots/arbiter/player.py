#!/usr/bin/env python
import asyncio
import shlex
import logging
from asyncio import subprocess as sp
from parser import *

BOT_TIMEOUT = 2  # seconds

class Player:
    """
    When `run_in_shell` is `True`, cmd should be a string, otherwise cmd should
    be an array of strings. This is the same distinction the subprocess module
    makes with the `shell` flag.
    """
    def __init__(self, name, cmd, run_in_shell=False):
        self.name = name
        self.forts = set()
        self.marches = set()
        self.cmd = cmd
        self.run_in_shell = run_in_shell
        self.in_control = True
        self.warnings = []

    @asyncio.coroutine
    def start_process(self):
        if self.run_in_shell:
            cmd = ("{} {}".format(self.cmd, shlex.quote(self.name))
                   .encode('utf8'))
            logging.info('Starting command: {}'.format(cmd))
            self.process = yield from asyncio.create_subprocess_shell(
                cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        else:
            cmd = self.cmd + [self.name]
            logging.info('Starting command: {}'.format(cmd))
            self.process = yield from asyncio.create_subprocess_exec(
                *cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

    @asyncio.coroutine
    def stop_process(self):
        try:
            self.process.kill()
        except ProcessLookupError:
            pass
        stderr = yield from self.process.stderr.read()
        if stderr:
            stderr = stderr.decode('utf8')
            self.warning('Stderr of {} was {}'.format(self.name, stderr))
        try:
            self.process._transport.close()
        except ProcessLookupError:
            logging.warning('Error when closing {}'.format(self.process))
            # if the process doesn't exist, it it probably closed, right?
            pass

    def capture(self, fort):
        if fort.owner:
            fort.owner.forts.remove(fort)
        fort.owner = self
        self.forts.add(fort)

    def is_defeated(self):
        return not self.in_control or (not self.forts and not self.marches)

    def remove_control(self):
        logging.info('Removing control from {}'.format(self.name))
        self.in_control = False

    @asyncio.coroutine
    def orders(self, game):
        # Send current state
        state = show_visible(self.forts)
        encoded = (state + '\n').encode('utf-8')
        self.process.stdin.write(encoded)
        try:
            yield from self.process.stdin.drain()
        except ConnectionResetError:
            self.error('{} stopped unexpectedly'.format(self.name))
            return []

        # Read bot's marches
        try:
            coroutine = async_read_section(self.process.stdout)
            section = yield from asyncio.wait_for(coroutine, BOT_TIMEOUT)
            marches = (parse_command(game, self, line) for line in section)
            return marches
        except asyncio.TimeoutError:
            self.error('{} timed out'.format(self.name))
            return []
        except ValueError:
            self.error('{} gave a syntax error'.format(self.name))
            return []
        except EOFError:
            self.error('{} stopped writing unexpectedly'.format(self.name))
            return []

    def warning(self, message):
        if message not in self.warnings:
            logging.warning(message)
            self.warnings.append(message)

    def error(self, message):
        logging.error(message)
        self.warnings.append('ERROR: {}'.format(message))
        self.remove_control()

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Player {name}>'.format(**self.__dict__)
