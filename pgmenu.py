import abc
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

class MenuElement(object):
    """Base class for all Menu objects"""
    __metaclass__ = abc.ABCMeta
    selectable = True
    label = None
    @abc.abstractmethod
    def draw(self, screen, x, y):
        """Draw the menu object on the screen"""
        return

    def set_font(self, font_size):
        if self.label is None:
            raise AttributeError('label string not set for MenuElement')
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)
        self.text = self.font.render(self.label, True, YELLOW)

class Label(MenuElement):
    selectable = False
    def __init__(self, label):
        self.label = label

    def draw(self, screen, x, y):
        screen.blit(self.text, [x, y])


class Button(MenuElement):
    selectable = True
    def __init__(self, label, func=None, *args, **kwargs):
        self.label = label
        self.func = func
        self.args = args
        self.kwargs = kwargs

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

    def push(self, *args, **kwargs):
        if self.func is not None:
            self.func(*self.args+args, **dict(self.kwargs, **kwargs))


class Menu(object):
    INDENT = 100
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.win_height = window_height
        self.win_width = window_width
        self.elements = []
        self.selection = 0
        self.position = 0
        self.top_showing = 0

        self.font_size = window_height // ITEMS_PER_PAGE

        self.font = pygame.font.Font(None, self.font_size)
        sample_text = self.font.render('sample', True, (0,0,0))
        dims = sample_text.get_bounding_rect()
        self.block_size = dims[3] - dims[1] + self.font_size
        self.max_on_screen = self.win_height / self.font_size

    def next_selectable(self):
        index = self.selection + 1
        while (index < len(self.elements) and
               not self.elements[index].selectable):
            index += 1

        if index >= len(self.elements):
            return self.selection
        else:
            return index

    def prev_selectable(self):
        index = self.selection - 1
        while (index >= 0 and
               not self.elements[index].selectable):
            index -= 1

        if index >= len(self.elements):
            return self.selection
        else:
            return index

    def __move_down(self):
        if self.selection == len(self.elements) - 1:
            return
        movement = self.next_selectable() - self.selection
        self.selection += movement
        if self.position < self.max_on_screen - 1:
            self.position += movement
        else:
            self.top_showing += movement

    def __move_up(self):
        if self.selection == 0:
            return
        movement = self.selection - self.prev_selectable()
        self.selection -= movement
        if self.position > 0:
            self.position -= movement
        else:
            self.top_showing -= movement

    def move_down(self, count=1):
        for _ in range(count):
            self.__move_down()

    def move_up(self, count=1):
        for _ in range(count):
            self.__move_up()

    def page_up(self):
        self.move_up(ITEMS_PER_PAGE-1)

    def page_down(self):
        self.move_down(ITEMS_PER_PAGE-1)

    def push(self, *args, **kwargs):
        """Push the currently selected button, calling it's
        function, with any optional additional args.

        """
        self.elements[self.selection].push(*args, **kwargs)

    def draw(self):
        """Draw only the elements that fit on the screen, and the cursor"""
        # calculate the dimensions of the button to draw the cursor
        button_dimensions = self.elements[self.selection].dimensions
        button_dimensions[0] += self.INDENT
        button_dimensions[1] += self.position * self.font_size
        pygame.draw.rect(self.screen, PALE_BLUE, button_dimensions)
        
        # draw all elements that fit on the screen
        for index, button in enumerate(
            self.elements[self.top_showing:
                         self.top_showing+self.max_on_screen]):
            button.draw(self.screen, self.INDENT, (index)*self.font_size)

    def add_element(self, button):
        button.set_font(self.font_size)
        self.elements.append(button)

