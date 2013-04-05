import gtk

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

def screen_resolution():
    window = gtk.Window()
    screen = window.get_screen()
    return screen.get_width(), screen.get_height()


class Button(object):
    def __init__(self, label, func=None, *args):
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

    def __move_down(self):
        if self.selection == len(self.buttons) - 1:
            return
        self.selection += 1
        if self.position < self.max_on_screen - 1:
            self.position += 1
        else:
            self.top_showing += 1

    def __move_up(self):
        if self.selection == 0:
            return
        self.selection -= 1
        if self.position > 0:
            self.position -= 1
        else:
            self.top_showing -= 1

    def move_down(self, count=1):
        for _ in range(count):
            self.__move_down()

    def move_up(self, count=1):
        for _ in range(count):
            self.__move_up()

    def page_up(self):
        self.move_up(ITEMS_PER_PAGE)

    def page_down(self):
        self.move_down(ITEMS_PER_PAGE)

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

