import subprocess
import os
import re

import pygame
from pygame.locals import *

import config

def rom_file_paths(location=config.ROM_FILE_PATH):
    rom_files = []
    for dirname, dirnames, filenames in os.walk(location):
        for filename in filenames:
            if filename[-4:] in ('.nes', '.zip', '.fds', '.nsf'):
                rom_files.append(os.path.join(dirname, filename))
    
    rom_files.sort(key=lambda s: s.lower())
    return rom_files


def run_emulator(rom_file_path):
    subprocess.call(config.EMULATOR + config.EMULATOR_FLAGS + rom_file_path,
                    shell=True)


def switch_to_emulator(window_size, rom_file_path):
    pygame.display.set_mode(window_size)
    run_emulator(rom_file_path)
    pygame.display.set_mode(window_size, FULLSCREEN)
