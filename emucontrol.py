import subprocess
import os
import re
import logging
import sys

import pygame
from pygame.locals import *

import config

NO_STATE = 99

def rom_file_paths(location=config.ROM_FILE_PATH):
    """Return a list of paths to roms in the 'location' directory
    and all subdirectories, sorted by name.  The subdirectory path
    is included in the name when sorting.

    """
    rom_files = []
    for dirname, dirnames, filenames in os.walk(location):
        for filename in filenames:
            if filename[-4:] in ('.nes', '.zip', '.fds', '.nsf'):
                rom_files.append(os.path.join(dirname, filename))
    
    rom_files.sort(key=lambda s: s.lower())
    return rom_files


class EmuController(object):
    def __init__(self):
        self.rom = None
        self.load_state = NO_STATE
        self.save_save = NO_STATE
        self.periodic_saves = True

    def set_rom(rom):
        self.rom = rom

    def set_load(state):
        self.load_state = state

    def set_save(state):
        self.save_state = state


    def run_emulator(self):
        if self.rom is None:
            raise AttributeError('No rom set for Emulator to run.')

        cmd = config.EMULATOR + config.EMULATOR_FLAGS
        cmd += ' --loadstate {0} --savestate {1} '.format(
            self.load_state, self.save_state)
        cmd += ' --periodicsaves {0} '.format(int(self.periodic_saves))
        cmd += self.rom
        logging.info('Starting emulator with command %s', cmd)
        subprocess.call(cmd, shell=True)
