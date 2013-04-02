import pygame
from pygame.locals import *
pygame.init()

BLACK = (0, 0, 0)
WHITE = (0xFF, 0xFF, 0xFF)
GREEN = (0, 0xFF, 0)
RED  = (0xFF, 0, 0)

YELLOW = (255, 255, 153)
PALE_BLUE = (153,102,255)

ITEMS_PER_PAGE = 20

class Button(object):
    def __init__(self, label, func, *args):
        self.label = label
        self.func = func
        self.args = args


    def set_font(self, font_size):
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)
        self.text = self.font.render(self.label, True, YELLOW)

    @property
    def dimensions(self):
        dims = self.text.get_bounding_rect()[:]
        padding = abs(self.font.get_descent())
        dims[0] -= padding
        dims[1] -= padding
        dims[2] += padding * 2
        dims[3] += padding * 2
        return dims

    @property
    def block_size(self):
        dims = self.text.get_bounding_rect()
        return dims[3] - dims[1] + self.font_size


    def draw(self, screen, x, y):
        screen.blit(self.text, [x, y])

    def push(self, *args):
        if self.func is not None:
            self.func(*(self.args + args))


class Cursor(object):
    def __init__(self, color):
        pass


class Menu(object):
    indent = 50
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.win_height = window_height
        self.win_width = window_width
        self.buttons = []
        self.selection = 0
        self.position = 0
        self.top_showing = 0

        self.font_size = window_height // ITEMS_PER_PAGE

        self.font = pygame.font.Font(None, self.font_size)
        sample_text = self.font.render('sample', True, (0,0,0))
        dims = sample_text.get_bounding_rect()
        self.block_size = dims[3] - dims[1] + self.font_size
        self.max_on_screen = self.win_height / self.font_size

    def move_down(self):
        if self.selection == len(self.buttons) - 1:
            return
        self.selection += 1
        if self.position < self.max_on_screen - 1:
            self.position += 1
        else:
            self.top_showing += 1

    def move_up(self):
        if self.selection == 0:
            return
        self.selection -= 1
        if self.position > 0:
            self.position -= 1
        else:
            self.top_showing -= 1

    def push(self):
        self.buttons[self.selection].push()

    def draw(self):
        button_dimensions = self.buttons[self.selection].dimensions
        button_dimensions[0] += Menu.indent
        button_dimensions[1] += self.position * self.font_size

        pygame.draw.rect(self.screen, PALE_BLUE, button_dimensions)
        for index, button in enumerate(
            self.buttons[self.top_showing:
                         self.top_showing+self.max_on_screen]):
            button.draw(self.screen, Menu.indent, (index)*self.font_size)

    def add_button(self, button):
        button.set_font(self.font_size)
        self.buttons.append(button)


import os
import re
import subprocess
import gtk

import config

def screen_resolution():
    window = gtk.Window()
    screen = window.get_screen()
    return screen.get_width(), screen.get_height()

def rom_file_paths(location):
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

if __name__ == '__main__':
    window_size = screen_width, screen_height = screen_resolution()
    
    pygame.mouse.set_visible(False)

    screen = pygame.display.set_mode(window_size, FULLSCREEN)
    pygame.display.update()

    main_menu = Menu(screen, screen_width, screen_height)

    # add all rom buttons
    for rom_file_path in rom_file_paths('/home/ryan/nes_rom_files/'):
        # get just the name of the rom (without path or extension) and
        game_name = rom_file_path.split('/')[-1].split('.')[0]
        # change to uppercase, replace all underscores with spaces
        game_name = game_name.upper().replace('_', ' ')
        rom_path_escaped = re.escape(rom_file_path)
        main_menu.add_button(Button(game_name, switch_to_emulator, 
                                    window_size, rom_path_escaped))


    pygame.display.set_caption("Some Window Title")
    pygame.key.set_repeat(250, 15)
    done = False

    screen.fill(BLACK)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_UP:
                    main_menu.move_up()
                elif event.key == pygame.K_DOWN:
                    main_menu.move_down()
                elif event.key in (K_a, K_RETURN):
                    main_menu.push()
                elif event.key == pygame.K_ESCAPE:
                    done = True

            elif event.type == pygame.QUIT:
                done = True
            else:
                print event

        # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT
        
        # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT
        # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        screen.fill(BLACK)
        main_menu.draw(screen)
        pygame.display.update()
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
        # Limit to 20 frames per second
        pygame.time.wait(8)

    pygame.quit()
