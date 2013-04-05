import time

import pygame

class Gamepad(object):
    RELEASE_DELAY = 0.250 #ms
    AXIS_DELAY = 2500
    QUIT = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    A = 5
    B = 6
    START = 7
    SELECT = 8
    DISCONNECTED = 9
    def __init__(self, js_num, *args, **kwargs):
        self.js = pygame.joystick.Joystick(js_num, *args, **kwargs)
        self.js_num = js_num
        self.js.init()
        self.done = False

    def actions(self):
        delay_y_current = False
        delay_y_next = True
        prev_y_time = 0
        self.wait_for_all_buttons_released = False
        self.wait_until = 0

        neutral = True
        pressed = 0
        last_update = pygame.time.get_ticks()

        while not self.done:
            for event in pygame.event.get():
                pass

            #pygame.joystick.quit()
            #pygame.joystick.init()
            #while pygame.joystick.get_count() == 0:
            #    yield self.DISCONNECTED
            #    pygame.joystick.quit()
            #    pygame.joystick.init()

            #self.js = pygame.joystick.Joystick(self.js_num)
            #self.js.init()

            x_axis, y_axis = (self.js.get_axis(i) for i in range(2))
            b_a, b_b, b_select, b_start = (self.js.get_button(i)
                                           for i in (0, 1, 8, 9))
            if all((b_a, b_b, b_select, b_start)):
                self.wait_for_all_buttons_released = True
                self.wait_until = time.time() + self.RELEASE_DELAY
            
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

                if pressed > self.AXIS_DELAY:
                    move = True

                if move:
                    if y_axis > 0.5:
                        yield self.DOWN
                    elif y_axis < -0.5:
                        yield self.UP

                    last_update = pygame.time.get_ticks()
                else:
                    yield None
            if y_axis == 0:
                if x_axis > 0.5:
                    yield self.RIGHT
                elif x_axis < -0.5:
                    yield self.LEFT

                
    def stop(self):
        self.done = True

    def wait_for_release(self):
        self.wait_for_all_buttons_released = True
        self.wait_until = time.time() + self.RELEASE_DELAY
