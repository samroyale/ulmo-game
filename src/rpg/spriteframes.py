#!/usr/bin/env python

import view

from view import DOWN

DIRECTION = "direction"

class SpriteFrames:
    
    def __init__(self, frameSkip = None):
        self.frameSkip = frameSkip
        self.frameCount = 0
        self.frameIndex = 0

    def advanceFrameIndex(self, increment = 1):
        if increment and self.frameSkip:
            self.frameCount = (self.frameCount + increment) % self.frameSkip
            if self.frameCount == 0:
                self.frameIndex = (self.frameIndex + 1) % self.numFrames
                return self.frameIndex
        return None
    
    def repairCurrentFrame(self):
        pass
    
    def advanceFrame(self, increment = 1, **kwargs):
        pass

    def getState(self):
        return self.frameCount, self.frameIndex, DOWN

    def setState(self, spriteFrames):
        self.frameCount, self.frameIndex, direction = spriteFrames.getState() 
        return self   
            
class StaticFrames(SpriteFrames):
    
    def __init__(self, animationFrames, frameSkip = None):
        SpriteFrames.__init__(self, frameSkip)
        self.virginAnimationFrames = animationFrames
        self.animationFrames = view.copyStaticFrames(animationFrames)
        self.numFrames = len(self.animationFrames)

    def repairCurrentFrame(self):
        lastImage = self.animationFrames[self.frameIndex]
        lastImage.blit(self.virginAnimationFrames[self.frameIndex], (0, 0))

    def advanceFrame(self, increment = 1, **kwargs):
        newFrameIndex = self.advanceFrameIndex(increment)
        return self.animationFrames[self.frameIndex], newFrameIndex
    
class DirectionalFrames(SpriteFrames):
    
    def __init__(self, animationFrames, frameSkip = None):
        SpriteFrames.__init__(self, frameSkip)
        self.virginAnimationFrames = animationFrames
        self.animationFrames = view.copyMovementFrames(animationFrames)
        self.numFrames = len(animationFrames[DOWN])
        self.direction = DOWN

    def repairCurrentFrame(self):
        lastImage = self.animationFrames[self.direction][self.frameIndex]
        lastImage.blit(self.virginAnimationFrames[self.direction][self.frameIndex], (0, 0))
        
    def advanceFrame(self, increment = 1, **kwargs):
        newFrameIndex = self.advanceFrameIndex(increment)
        if DIRECTION in kwargs:
            self.direction = kwargs[DIRECTION]
        return self.animationFrames[self.direction][self.frameIndex], newFrameIndex

    def getState(self):
        return self.frameCount, self.frameIndex, self.direction

    def setState(self, spriteFrames):
        self.frameCount, self.frameIndex, self.direction = spriteFrames.getState()
        return self   
            
