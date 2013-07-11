"""Paths to resources used for running the emulator"""

EMULATOR = 'fceux'
EMULATOR_FLAGS = (' '
                  ' --special 0 ' # no special filter
                  '--fullscreen 1 ' # fullscreen mode
                  '--autoscale 1 ' # scale the image size to fill the screen
                  '--keepratio 0 ' # keep the x and y ratio (idk why 0 works)
                  '--inputdisplay 0 ' # don't show what buttons are pushed
                  '--showfps 0 ' # don't display fps
                  '--nofscursor 1 ' # don't display cursor in fullscreen
                  '--clipsides 1 '
                  '--4buttonexit 1 ' # exit on a+b+select+start
                  '--nospritelim 1 ' # prevent missing pixels
                  #'--nogui 1 ' # don't draw the window stuff
                  ' ') 

ROM_FILE_PATH = '/home/ryan/nes_rom_files'
