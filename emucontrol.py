import subprocess
import os
import re
import logging

import pygame
from pygame.locals import *

import config

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



def switch_to_emulator(window_size, rom_file_path, autoload=99, autosave=99):
    """Switch the fullscreen menu to windowed mode and open the
    emulator with the rom provided.  After it exits, make the menu
    fullscreen again

    """
    pygame.display.set_mode(window_size)
    cmd = config.EMULATOR + config.EMULATOR_FLAGS
    cmd += ' --autosavestate {0} --autoloadstate {1} '.format(autosave,
                                                              autoload)
    cmd += rom_file_path
    logging.info('Starting emulator with command %s', cmd) 
    subprocess.call(cmd, shell=True)
    pygame.display.set_mode(window_size, FULLSCREEN)
