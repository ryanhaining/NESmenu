import re
import sys
import logging
import time

import pygame
from pygame.locals import *

import pgmenu
import config
import nesgamepad
import emucontrol

# get the dimensions of the screen
window_size = screen_width, screen_height = pgmenu.screen_resolution()

# hide the mouse
pygame.mouse.set_visible(False)

# create the screen for the menu
screen = pygame.display.set_mode(window_size, FULLSCREEN)
pygame.display.update()

# menu for all roms
main_menu = pgmenu.Menu(screen, screen_width, screen_height)

# menu to show when no controller can be found
insert_controller_menu = pgmenu.Menu(screen, screen_width, screen_height)
insert_controller_menu.add_button(pgmenu.Button('PLEASE INSERT CONTROLLER'))

def redraw(menu):
    screen.fill(pgmenu.BLACK)
    menu.draw()
    pygame.display.update()
    pygame.time.wait(5)

def wait_for_controller():
    while pygame.joystick.get_count() == 0:
        pygame.joystick.quit()
        print 'no controller connected'
        time.sleep(0.1)
        redraw(insert_controller_menu)
        pygame.joystick.init()


pygame.joystick.init()
wait_for_controller()
gamepad = nesgamepad.Gamepad(0)

def quit_menu(controller):
    controller.done = True

#add the quit button
main_menu.add_button(pgmenu.Button("QUIT", quit_menu, gamepad))

# add all rom buttons
for rom_file_path in emucontrol.rom_file_paths():
    # get just the name of the rom (without path or extension) and
    game_name = ''.join(rom_file_path.split('/')[-1].split('.')[:-1])
    # change to uppercase, replace all underscores with spaces
    game_name = game_name.upper().replace('_', ' ')
    rom_path_escaped = re.escape(rom_file_path)
    main_menu.add_button(pgmenu.Button(game_name,
                                       emucontrol.switch_to_emulator,
                                       window_size, rom_path_escaped))

redraw(main_menu)

for action in gamepad.actions():
    if action == gamepad.UP:
        main_menu.move_up()
    elif action == gamepad.DOWN:
        main_menu.move_down()
    elif action in (gamepad.A, gamepad.START):
        main_menu.push()
        gamepad.wait_for_release()
    elif action == gamepad.RIGHT:
        main_menu.page_down()
    elif action == gamepad.LEFT:
        main_menu.page_up()
    elif action == gamepad.DISCONNECTED:
        print 'gamepad disconnected... wating for reconnect'
        wait_for_controller()

    redraw(main_menu)

pygame.quit()
