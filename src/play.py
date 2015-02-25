#! /usr/bin/env python

from pygame.locals import KEYDOWN, K_ESCAPE, K_x, QUIT

import pygame

"""
If using an older Raspberry Pi distro, you might need to run the following commands to get working sound:

sudo apt-get install alsa-utils
sudo modprobe snd_bcm2835
"""

# initialise pygame before we import anything else
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()

import rpg.states

def playMain():
    # get the first state
    currentState = rpg.states.showTitle(True)
    # start the main loop
    clock = pygame.time.Clock()    
    while True:
        clock.tick(rpg.states.FRAMES_PER_SEC)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            if event.type == KEYDOWN and event.key == K_x:
                # toggle sound
                rpg.states.soundHandler.toggleSound()
                rpg.states.musicPlayer.toggleMusic()
        # detect key presses    
        keyPresses = pygame.key.get_pressed()
        # delegate key presses to the current state
        newState = currentState.execute(keyPresses)
        # flush sounds
        rpg.states.soundHandler.flush()
        # change state if necessary
        if newState:
            currentState = newState

# this calls the playMain function when this script is executed
if __name__ == '__main__': playMain()
