#!/usr/bin/env python

import re
import sys
import logging
import time

import pygame
from pygame.locals import FULLSCREEN

import pgmenu
import config
import nesgamepad
import emucontrol

logging.basicConfig(logLevel=logging.INFO)

# get the dimensions of the screen
window_size = screen_width, screen_height = pgmenu.screen_resolution()

# hide the mouse
pygame.mouse.set_visible(False)

# create the screen for the menu
screen = pygame.display.set_mode(window_size, FULLSCREEN)
pygame.display.update()

# menu to show when no controller can be found
insert_controller_menu = pgmenu.RootMenu(screen, screen_width, screen_height)
insert_controller_menu.main_menu.add_element(
    pgmenu.Label('PLEASE INSERT CONTROLLER'))

def redraw(menu):
    """Draw the given menu on the screen"""
    screen.fill(pgmenu.BLACK)
    menu.display()
    pygame.display.update()
    pygame.time.wait(5)

def wait_for_controller():
    """Wait for at least one controller to be inserted"""
    while pygame.joystick.get_count() == 0:
        pygame.joystick.quit()
        print 'no controller connected'
        time.sleep(0.1)
        redraw(insert_controller_menu)
        pygame.joystick.init()


pygame.joystick.init()
wait_for_controller()

gamepad = nesgamepad.Gamepad(0)

def set_game(emu_controller, root_menu, next_menu, rom):
    emu_controller.rom = rom
    root_menu.forward_menu(next_menu)

def launch(emu_controller, root_menu, load_state, save_state):
    emu_controller.periodic_saves = save_state != emucontrol.NO_STATE
    emu_controller.load_state = load_state
    emu_controller.save_state = save_state
    pygame.display.set_mode(window_size)
    emu_controller.run_emulator()
    pygame.display.set_mode(window_size, FULLSCREEN)
    root_menu.top_menu()

def new_game(emu_controller, root_menu, save_state):
    launch(emu_controller, root_menu, emucontrol.NO_STATE, save_state)

def continue_game(emu_controller, root_menu, load_state, save_state):
    launch(emu_controller, root_menu, load_state, save_state)


fceux_controller = emucontrol.EmuController()

# menu for all roms
game_menu = pgmenu.RootMenu(screen, screen_width, screen_height)

#add the quit button
game_menu.main_menu.add_element(pgmenu.Button("SHUTDOWN SYSTEM", gamepad.stop))

game_menu.main_menu.add_element(pgmenu.Label("Games:"))

# SubMenus for selecting a save slot
new_menu = pgmenu.SubMenu('NEW GAME', game_menu)
continue_menu = pgmenu.SubMenu('CONTINUE', game_menu)

for menu in (new_menu, continue_menu):
    menu.add_element(pgmenu.Label('Select a Save Slot to use:'))

new_menu.add_element(
        pgmenu.Button('NO SAVE', new_game, fceux_controller,
                      game_menu, emucontrol.NO_STATE))

for i in range(10):
    continue_menu.add_element(
        pgmenu.Button('SLOT {0}'.format(i+1), continue_game, fceux_controller,
                      game_menu, i, i))
    new_menu.add_element(
        pgmenu.Button('SLOT {0}'.format(i+1), new_game, fceux_controller,
                      game_menu, i))

new_or_continue_menu = pgmenu.SubMenu('', game_menu)
new_or_continue_menu.add_element(new_menu)
new_or_continue_menu.add_element(continue_menu)
                                              

# add all rom buttons
for rom_file_path in emucontrol.rom_file_paths():
    # get just the name of the rom (without path or extension) and
    game_name = ''.join(rom_file_path.split('/')[-1].split('.')[:-1])
    # change to uppercase, replace all underscores with spaces
    game_name = game_name.upper().replace('_', ' ')
    rom_path_escaped = re.escape(rom_file_path)
    game_menu.main_menu.add_element(
        pgmenu.Button(game_name, set_game, fceux_controller, game_menu, 
                      new_or_continue_menu, rom_path_escaped))

redraw(game_menu)

for action in gamepad.actions():
    if action == gamepad.UP:
        game_menu.move_up()
    elif action == gamepad.DOWN:
        game_menu.move_down()
    elif action in (gamepad.A, gamepad.START):
        game_menu.push()
        gamepad.wait_for_release()
    elif action == gamepad.B:
        game_menu.back_menu()
        gamepad.wait_for_release()
    elif action == gamepad.RIGHT:
        game_menu.page_down()
    elif action == gamepad.LEFT:
        game_menu.page_up()
    elif action == gamepad.DISCONNECTED:
        print 'gamepad disconnected... wating for reconnect'
        wait_for_controller()

    redraw(game_menu)

pygame.quit()
