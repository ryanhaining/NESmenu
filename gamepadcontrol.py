import re
import sys
import logging
import time

import pygame
from pygame.locals import *

import pgmenu
import config

window_size = screen_width, screen_height = pgmenu.screen_resolution()

pygame.mouse.set_visible(False)


screen = pygame.display.set_mode(window_size, FULLSCREEN)
pygame.display.update()

main_menu = pgmenu.Menu(screen, screen_width, screen_height)


pygame.display.set_caption("NES Rom Menu")
pygame.key.set_repeat(250, 15)
done = False

def redraw():
    screen.fill(pgmenu.BLACK)
    main_menu.draw()
    pygame.display.update()
    pygame.time.wait(5)

class NESGamepad(object):
    DELAY_TIME = 0.250 #ms
    QUIT = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    A = 5
    B = 6
    START = 7
    SELECT = 8
    def __init__(self, *args, **kwargs):
        self.js = pygame.joystick.Joystick(*args, **kwargs)
        self.js.init()
        self.done = False

    def actions(self):
        delay_y_current = False
        delay_y_next = True
        prev_y_time = 0
        self.wait_for_all_buttons_released = False
        self.wait_until = 0

        delay = 2500
        neutral = True
        pressed = 0
        last_update = pygame.time.get_ticks()

        while not self.done:
                for event in pygame.event.get():
                    pass

                x_axis, y_axis = (self.js.get_axis(i) for i in range(2))
                b_a, b_b, b_select, b_start = (self.js.get_button(i)
                                               for i in (0, 1, 8, 9))
                if all((b_a, b_b, b_select, b_start)):
                    self.wait_for_all_buttons_released = True
                    self.wait_until = time.time() + self.DELAY_TIME
                
                if self.wait_for_all_buttons_released:
                    if time.time() < self.wait_until:
                        continue
                    else:
                        self.wait_for_all_buttons_released = False

                if b_b:
                    yield self.B
                elif b_a:
                    yield self.A
                elif b_select:
                    yield self.SELECT
                elif b_start:
                    yield self.START
                else:
                    move = False
                    if y_axis == 0:
                        neutral = True
                        pressed = 0
                    else:
                        if neutral:
                            move = True
                            neutral = False
                        else:
                            pressed += pygame.time.get_ticks() - last_update

                    if pressed > delay:
                        move = True
                        #pressed -= delay

                    if move:
                        if y_axis > 0.5:
                            yield self.DOWN
                        elif y_axis < -0.5:
                            yield self.UP

                        last_update = pygame.time.get_ticks()
                    else:
                        yield None

                
    def stop(self):
        self.done = True

    def wait_for_release(self):
        self.wait_for_all_buttons_released = True
        self.wait_until = time.time() + self.DELAY_TIME

y_delay = True
gamepad = NESGamepad(0)
#pygame.time.set_timer(pygame.USEREVENT, 20)


def quit(controller):
    controller.done = True

#add the quit button
main_menu.add_button(pgmenu.Button("QUIT", quit, gamepad))

# add all rom buttons
for rom_file_path in pgmenu.rom_file_paths(config.ROM_FILE_PATH):
    # get just the name of the rom (without path or extension) and
    game_name = ''.join(rom_file_path.split('/')[-1].split('.')[:-1])
    # change to uppercase, replace all underscores with spaces
    game_name = game_name.upper().replace('_', ' ')
    rom_path_escaped = re.escape(rom_file_path)
    main_menu.add_button(pgmenu.Button(game_name, pgmenu.switch_to_emulator, 
                                       window_size, rom_path_escaped))


redraw()

for action in gamepad.actions():
    if action == gamepad.UP:
        main_menu.move_up()
    elif action == gamepad.DOWN:
        main_menu.move_down()
    elif action in (gamepad.A, gamepad.START):
        main_menu.push()
        gamepad.wait_for_release()
    elif action == gamepad.B:
        done = True
        break

    # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT
    
    # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT
    # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT

    # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
    screen.fill(pgmenu.BLACK)
    main_menu.draw()
    pygame.display.update()

pygame.quit()
