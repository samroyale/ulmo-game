#! /usr/bin/env python

import os
import pygame

MUSIC_FOLDER = "music"

VOLUME_OFF = 0

DEFAULT_FADEOUT_MILLIS = 1000
LONG_FADEOUT_MILLIS = 6000

MUSIC_ON, MUSIC_OFF = True, False 
STATES = [MUSIC_ON, MUSIC_OFF, MUSIC_OFF]

TRACKS = {"title": ("ulmo-title.ogg", 0.6),
          "main": ("ulmo-main.ogg", 0.4)}

def getTrackAndVolume(name):
    if name in TRACKS:
        filename, volume = TRACKS[name]
        return os.path.join(MUSIC_FOLDER, filename), volume
    return None, None

"""
Plays, fades out and mutes music as required. Originally I intended to have different music for
different areas, but this proved quite tricky due to the way that fadeout blocks.
"""
class MusicPlayer:
    
    def __init__(self):
        self.musicEnabled = True if pygame.mixer.get_init() else False
        self.trackName = None
        self.volume = VOLUME_OFF
        self.state = 0
        
    def playTrack(self, name):
        if self.musicEnabled:
            if name == self.trackName:
                return
            self.fadeoutCurrentTrack(name)
            track, volume = getTrackAndVolume(name)
            if track:
                self.volume = volume
                if STATES[self.state]:
                    pygame.mixer.music.set_volume(self.volume)
                try:
                    pygame.mixer.music.load(track)
                    pygame.mixer.music.play(-1)
                except pygame.error:
                    print "Cannot load track: ", os.path.abspath(track)
                    
    def longFadeoutCurrentTrack(self, name = None):
        self.fadeoutCurrentTrack(name, LONG_FADEOUT_MILLIS)
                        
    def fadeoutCurrentTrack(self, name = None, millis = DEFAULT_FADEOUT_MILLIS):
        if self.musicEnabled:
            self.trackName = name
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(millis)        
            
    def toggleMusic(self):
        if self.musicEnabled:
            musicOn = STATES[self.state]
            self.state = (self.state + 1) % len(STATES)        
            if musicOn and not STATES[self.state]:
                pygame.mixer.music.set_volume(VOLUME_OFF)
                return
            if STATES[self.state] and not musicOn:
                pygame.mixer.music.set_volume(self.volume)
                return
 

