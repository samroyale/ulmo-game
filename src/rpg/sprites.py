#!/usr/bin/env python

import os
import pygame
import view

from pygame.locals import Rect
from view import SCALAR, TILE_SIZE

VELOCITY = 1
MOVE_UNIT = VELOCITY * SCALAR

# we may need to specify these on a sprite by sprite basis 
BASE_RECT_HEIGHT = 9 * SCALAR
BASE_RECT_EXTEND = 1 * SCALAR

SPRITES_FOLDER = "sprites"

NO_METADATA = {}
NO_MOVEMENT = (0, 0, NO_METADATA)

"""
Base sprite class that supports being masked by the map.
"""
class RpgSprite(pygame.sprite.Sprite):

    def __init__(self, spriteFrames, position = (0, 0)):
        pygame.sprite.Sprite.__init__(self)
        # properties common to all RpgSprites
        self.spriteFrames = spriteFrames
        self.position = [i * SCALAR for i in position]
        self.image, temp = self.spriteFrames.advanceFrame(0)
        # indicates if this sprite stands upright
        self.upright = True
        # indicates if this sprite is currently visible
        self.inView = False
        # indicates if this sprite is currently masked by any map tiles
        self.masked = False
        # indicates if this sprite should be removed on next update
        self.toRemove = False
        
    def setup(self, uid, rpgMap, eventBus):
        self.uid = uid
        self.rpgMap = rpgMap
        self.eventBus = eventBus
        
    def setTilePosition(self, tx, ty, level):
        self.tilePosition = (tx, ty)
        self.setPixelPosition(tx * TILE_SIZE + self.position[0],
                              ty * TILE_SIZE + self.position[1],
                              level)

    def setPixelPosition(self, px = 0, py = 0, level = None):
        # main rect
        self.rect = self.image.get_rect()
        # other rectangles as required by the game engine
        self.mapRect = self.image.get_rect()
        self.initBaseRect()
        # if required, move to the requested position
        if level != None:
            self.level = level
        if px > 0 or py > 0:
            self.doMove(px, py)
        
    def initBaseRect(self):
        baseRectWidth = self.mapRect.width 
        baseRectHeight = BASE_RECT_HEIGHT
        if hasattr(self, "baseRectSize"):
            baseRectWidth = self.baseRectSize[0]
            baseRectHeight = self.baseRectSize[1]
        baseRectTop = self.getBaseRectTop(baseRectHeight)
        baseRectLeft = (self.mapRect.width - baseRectWidth) / 2
        self.baseRect = Rect(baseRectLeft, baseRectTop, baseRectWidth, baseRectHeight)
        # print self.uid, self.mapRect, self.baseRect
        
    def getBaseRectTop(self, baseRectHeight):
        return self.mapRect.bottom - baseRectHeight
        
    def doMove(self, px, py):
        self.mapRect.move_ip(px, py)
        self.baseRect.move_ip(px, py)
        # a pseudo z order is used to test if one sprite is behind another
        self.z = self.calculateZ()

    def calculateZ(self):
        return int(self.mapRect.bottom + self.level * TILE_SIZE)
    
    def clearMasks(self):
        if self.masked:
            self.masked = False
            self.spriteFrames.repairCurrentFrame()
        
    def applyMasks(self):
        # masks is a map of lists, keyed on the associated tile points
        masks = self.rpgMap.getMasks(self)
        if len(masks) > 0:
            self.masked = True
            for tilePoint in masks:
                px = tilePoint[0] * view.TILE_SIZE - self.mapRect.left
                py = tilePoint[1] * view.TILE_SIZE - self.mapRect.top
                [self.image.blit(mask, (px, py)) for mask in masks[tilePoint]]
                
    def advanceFrame(self, increment, metadata):
        self.image, frameIndex = self.spriteFrames.advanceFrame(increment, **metadata)
        self.playSound(frameIndex)
        
    def playSound(self, frameIndex):
        pass
            
    def isIntersecting(self, sprite):
        if self != sprite and self.level == sprite.level and self.baseRect.colliderect(sprite.baseRect):
            return True
        return False;
        
    def processCollision(self, player):
        pass
    
    def processAction(self, player):
        pass
    
    def processMapExit(self):
        return False

"""
Base class for any sprites that aren't either the player or a fixed sprite.
"""
class OtherSprite(RpgSprite):
    
    def __init__(self, spriteFrames, position = (0, 0)):
        RpgSprite.__init__(self, spriteFrames, position)
        self.movement = None
    
    def update(self, player, visibleSprites, viewRect, increment, trigger = 1):
        # remove the sprite if required
        if self.toRemove:
            self.kill()
            return
        # otherwise apply movement
        px, py, metadata = self.getMovement(player, trigger)            
        self.doMove(px, py)
        # make self.rect relative to the view
        self.rect.topleft = (self.mapRect.left - viewRect.left,
                             self.mapRect.top - viewRect.top)
        if self.mapRect.colliderect(viewRect):
            # some part of this sprite is in view
            self.clearMasks()
            self.advanceFrame(increment, metadata)
            self.applyMasks()
            if not self.inView:
                self.inView = True
                self.add(visibleSprites)
            return
        # test if the sprite has exited the map completely
        if self.processMapExit():
            return
        # at this point we know the sprite is on the map but out of view 
        if self.inView:
            self.inView = False
            self.remove(visibleSprites)
    
    # initialises sprite movement and sets the tile position        
    def initMovement(self, level, tilePoints):
        self.setTilePosition(tilePoints[0][0], tilePoints[0][1], level)
        self.level = level
        self.tilePoints = tilePoints
            
    # base movement method - this is sufficient for static sprites only        
    def getMovement(self, player, trigger):
        return NO_MOVEMENT
                                   
"""
Sprite group that ensures pseudo z ordering for the sprites.  This works
because internally AbstractGroup calls self.sprites() to get a list of sprites
before it draws them.  I've overidden the sprites() method to return the
sprites in the correct order - this works, but I might be in trouble if the
internals of AbstractGroup ever changes.
"""
class RpgSprites(pygame.sprite.Group):
    
    def __init__(self, *sprites):
        pygame.sprite.AbstractGroup.__init__(self)
        self.add(*sprites)
        
    def sprites(self):
        # return the sprites sorted on their z field to ensure 
        # that they appear in the correct 'z' order
        return sorted(self.spritedict.keys(),
                      lambda sprite1, sprite2: sprite1.z - sprite2.z)
        
