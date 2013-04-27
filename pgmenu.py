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
    """Abstract Base Class for all Menu objects"""
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

class SubMenu(MenuElement):
    INDENT = 100
    selectable=True
    def __init__(self, label, root_menu):
        self.label = label
        self.root_menu = root_menu

        self.elements = []
        self.selection = 0
        self.position = 0
        self.top_showing = 0


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


        if index < 0:
            return self.selection
        else:
            return index


    def __move_down(self):
        if self.selection == len(self.elements) - 1:
            return
        movement = self.next_selectable() - self.selection
        self.selection += movement

        # TODO finish this v
        #self.position += movement
        #if self.position >= self.root_menu.max_on_screen:
        #    self.position = ITEMS_PER_PAGE - 1
        #    self.top_showing = self.selection - ITEMS_PER_PAGE
        # TODO finish this ^
        if self.position < self.root_menu.max_on_screen - 1:
            self.position += movement
        else:
            self.top_showing += movement

    def __move_up(self):
        if self.selection == 0:
            return
        movement = self.selection - self.prev_selectable()
        self.selection -= movement

        self.position -= movement
        if self.position < 0:
            # if it went past the top of the menu, reset the position
            # to the top
            self.position = 0
            self.top_showing = self.selection

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

    def push_selection(self, *args, **kwargs):
        """Push the currently selected element, calling it's
        function, with any optional additional args.

        """
        self.elements[self.selection].push()

    def push(self, *args, **kwargs):
        self.root_menu.forward_menu(self)

    def display(self):
        """Draw only the elements that fit on the screen, and the cursor"""
        # calculate the dimensions of the element to draw the cursor
        draw_cursor = True
        current_selection = self.selection
        if not self.elements[self.selection].selectable:
            self.move_down()
            draw_cursor = self.selection != current_selection

        if draw_cursor:
            element_dimensions = self.elements[self.selection].dimensions
            element_dimensions[0] += self.INDENT
            element_dimensions[1] += self.position * self.root_menu.font_size
            pygame.draw.rect(self.root_menu.screen, PALE_BLUE, 
                             element_dimensions)
        
        # draw all elements that fit on the screen
        for index, element in enumerate(
            self.elements[self.top_showing:
                         self.top_showing+self.root_menu.max_on_screen]):
            element.draw(self.root_menu.screen, self.INDENT, 
                         (index)*self.root_menu.font_size)

    def add_element(self, element):
        element.set_font(self.root_menu.font_size)
        self.elements.append(element)

    def draw(self, screen, x, y):
        screen.blit(self.text, [x, y])

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

    def reset(self):
        self.move_up(count=self.selection)


class RootMenu(object):
    def __init__(self, screen, window_width, window_height):
        #super(RootMenu, self).__init__(screen, window_width, window_height)
        # a stack for the depth into the menus and submenus
        # this must always contain at least the main menu
        self.main_menu = SubMenu('', self)
        self.menu_stack = [self.main_menu]

        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height

        # create the font used in displaying the text
        self.font_size = window_height // ITEMS_PER_PAGE
        self.font = pygame.font.Font(None, self.font_size)
        sample_text = self.font.render('sample', True, (0,0,0))
        dims = sample_text.get_bounding_rect()
        self.block_size = dims[3] - dims[1] + self.font_size
        self.max_on_screen = self.window_height / self.font_size

    def push(self):
        self.menu_stack[-1].push_selection()

    def back_menu(self):
        if len(self.menu_stack) > 1:
            # remove the top menu from the stack and set it's selection
            # its first item
            self.menu_stack.pop().reset()

    def forward_menu(self, menu):
        self.menu_stack.append(menu)

    def top_menu(self):
        del self.menu_stack[1:]
    
    def __getattr__(self, attr):
        return getattr(self.menu_stack[-1], attr)
    
