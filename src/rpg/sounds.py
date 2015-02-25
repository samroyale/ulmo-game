#!/usr/bin/env python

import os
import pygame

SOUNDS_FOLDER = "sounds"

BEETLE_SOUND_TICKS = 15

SOUNDS_ON, SOUNDS_OFF = True, False
STATES = [SOUNDS_ON, SOUNDS_ON, SOUNDS_OFF]

def getSound(name, volume):
    if pygame.mixer.get_init():
        soundPath = os.path.join(SOUNDS_FOLDER, name)
        sound = pygame.mixer.Sound(soundPath)
        sound.set_volume(volume)
        return sound
    return None

pickupSound = getSound("pickup.wav", 1.0)
doorSound = getSound("door.wav", 0.5)
checkpointSound = getSound("checkpoint.wav", 0.8)
swooshSound = getSound("swoosh.wav", 0.4)
lifeLostSound = getSound("lifelost.wav", 1.0)
endGameSound = getSound("endgame.wav", 0.6)
footstepSound = getSound("footstep.wav", 0.5)
waspSound = getSound("wasp.wav", 0.8)
beetleSound = getSound("beetle.wav", 0.2)
fallingSound = getSound("falling.wav", 0.2)
bladesSound = getSound("blades.wav", 0.4)
titleSound = getSound("title.wav", 0.8)
boatSound = getSound("waves.wav", 0.3)

"""
Listens for specific events and builds up a set of sounds that are played back
when flush is called.
"""
class SoundHandler:
    
    def __init__(self):
        self.sounds = set()
        # properties required for 
        self.nextSound = None
        self.ready = True
        self.state = 0
        self.count = 0
            
    def coinCollected(self, coinCollectedEvent):
        self.sounds.add(pickupSound)
        
    def keyCollected(self, keyCollectedEvent):
        self.sounds.add(pickupSound)
        
    def doorOpening(self, doorOpeningEvent):
        self.sounds.add(doorSound)
        
    def checkpointReached(self, checkpointEvent):
        self.sounds.add(checkpointSound)
        
    def playerFootstep(self, playerFootstepEvent):
        self.sounds.add(footstepSound)
        
    def mapTransition(self, mapTransitionEvent):
        self.sounds.add(swooshSound)
        
    def endGame(self, endGameEvent):
        self.sounds.add(endGameSound)
        
    def lifeLost(self, lifeLostEvent):
        self.sounds.add(lifeLostSound)
    
    def waspZooming(self, waspZoomingEvent):
        self.sounds.add(waspSound)
        
    def playerFalling(self, playerFallingEvent):
        self.sounds.add(fallingSound)
    
    def bladesStabbing(self, bladesStabbingEvent):
        self.sounds.add(bladesSound)

    def titleShown(self, titleShownEvent):
        self.sounds.add(titleSound)
    
    def gameStarted(self, gameStartedEvent):
        self.sounds.add(checkpointSound)
    
    def boatMoving(self, boatMovingEvent):
        self.sounds.add(boatSound)
        
    """
    Additional logic here to prevent a 'log jam' of beetle crawling sounds
    """    
    def beetleCrawling(self, beetleCrawlingEvent):
        # if we already have a next sound, ignore it
        if self.nextSound:
            return
        # if ready, add the sound to the set for immediate playback
        if self.ready:
            self.sounds.add(beetleSound)
            self.ready = False
            self.count = 0
            return
        # we're not ready yet - store the sound for later
        self.nextSound = beetleSound
        
    def handleNextSound(self):
        self.count = (self.count + 1) % BEETLE_SOUND_TICKS
        if self.count == 0:
            if self.nextSound:
                self.sounds.add(self.nextSound)
                self.nextSound = None
            else:
                self.ready = True
        
    def flush(self):
        self.handleNextSound()
        # play sounds
        for sound in self.sounds:
            if sound and STATES[self.state]:
                sound.play()
        self.sounds.clear()
        
    def toggleSound(self):
        self.state = (self.state + 1) % len(STATES)
        
