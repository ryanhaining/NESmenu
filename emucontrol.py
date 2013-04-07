import subprocess
import os
import re
import logging

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
    def __init__(self, window_size):
        self.window_size = window_size
        self.rom = None
        self.load_state = NO_STATE
        self.save_save = NO_STATE

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
        cmd += ' --autoloadstate {0} --autosavestate {1} '.format(
            self.load_state, self.save_state)
        cmd += self.rom
        logging.info('Starting emulator with command %s', cmd) 
        subprocess.call(cmd, shell=True)

    def switch_to_emulator(self):
        """Switch the fullscreen menu to windowed mode and open the
        emulator with the rom provided.  After it exits, make the menu
        fullscreen again

        """
        pygame.display.set_mode(self.window_size)
        self.run_emulator()
        pygame.display.set_mode(self.window_size, FULLSCREEN)
