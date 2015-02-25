#!/usr/bin/env python

from sprites import *

from view import VIEW_WIDTH, VIEW_HEIGHT

import font

"""
Defines a sprite that is fixed on the game display.  Note that this class of
sprite does not extend RpgSprite. 
"""
class FixedSprite(pygame.sprite.Sprite):

    def __init__(self, position = (0, 0)):
        pygame.sprite.Sprite.__init__(self)
        x, y = 0, 0
        if position[0] < 0:
            x = VIEW_WIDTH + position[0] * SCALAR
        else:
            x = position[0] * SCALAR
        if position[1] < 0:
            y = VIEW_HEIGHT + position[1] * SCALAR
        else:
            y = position[1] * SCALAR
        self.position = (x, y)
        
    def setImage(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        
class FixedCoin(FixedSprite):

    initialImage = None
    
    def __init__(self, position = (0, 0)):
        if FixedCoin.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "small-coin.png")
            FixedCoin.initialImage = view.loadScaledImage(imagePath)
        FixedSprite.__init__(self, position)
        self.setImage(view.createDuplicateSpriteImage(FixedCoin.initialImage))

class CoinCount(FixedSprite):
    
    def __init__(self, count = 0, position = (0, 0)):
        FixedSprite.__init__(self, position)
        self.font = font.NumbersFont()
        self.count = count;
        self.newImage()
                
    def newImage(self):
        newImage = self.font.getTextImage(str(self.count))
        self.setImage(newImage)
        
    def incrementCount(self, n = 1):
        self.count += n
        self.newImage()
        print "coins:", self.count

    def setCount(self, count):
        self.count = count
        self.newImage()

class KeyCount(FixedSprite):
    
    initialImage = None
    
    def __init__(self, count = 0, position = (0, 0)):
        if KeyCount.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "small-key.png")
            KeyCount.initialImage = view.loadScaledImage(imagePath)
        self.keyImage = view.createDuplicateSpriteImage(KeyCount.initialImage)
        FixedSprite.__init__(self, position)
        self.count = count
        self.newImage()
        
    def newImage(self):
        dimensions = (self.count * 8 * SCALAR, 8 * SCALAR)
        newImage = view.createTransparentRect(dimensions)
        for i in range(self.count):
            px = i * 8 * SCALAR
            newImage.blit(self.keyImage, (px, 0))
        self.setImage(newImage)
        self.rect.left = VIEW_WIDTH - (3 + self.count * 8) * SCALAR

    def incrementCount(self, n = 1):
        self.count += n
        self.newImage()
        print "keys:", self.count

    def setCount(self, count):
        self.count = count
        self.newImage()

class Lives(FixedSprite):
    
    initialImage = None
    
    def __init__(self, count = 0, position = (0, 0)):
        if Lives.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "life.png")
            Lives.initialImage = view.loadScaledImage(imagePath)
        self.livesImage = view.createDuplicateSpriteImage(Lives.initialImage)
        FixedSprite.__init__(self, position)
        self.count = count
        self.newImage()
        
    def newImage(self):
        dimensions = (self.count * 8 * SCALAR, 8 * SCALAR)
        newImage = view.createTransparentRect(dimensions)
        for i in range(self.count):
            px = i * 8 * SCALAR
            newImage.blit(self.livesImage, (px, 0))
        self.setImage(newImage)

    def incrementCount(self, n = 1):
        self.count += n
        if (self.count < 0):
            return
        self.newImage()
        print "lives:", self.count
        
    def noneLeft(self):
        return self.count < 0

class CheckpointIcon(FixedSprite):

    initialImage = None
    
    def __init__(self, position = (0, 0)):
        if CheckpointIcon.initialImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "small-check.png")
            CheckpointIcon.initialImage = view.loadScaledImage(imagePath)
        FixedSprite.__init__(self, position)
        self.onImage = view.createDuplicateSpriteImage(CheckpointIcon.initialImage)
        self.offImage = view.createTransparentRect((0, 0))
        self.setImage(self.offImage)
        self.on = False
        self.ticks = -1
        self.tickLimit = 100 // VELOCITY
        self.tickToggle = 20 // VELOCITY
        
    def activate(self):
        self.ticks = 0
        
    def update(self):
        # test if the icon is active
        if self.ticks < 0:
            return
        # test if the icon cycle has finished
        if self.ticks > self.tickLimit:
            self.ticks = -1
            return
        # update icon
        if self.ticks % self.tickToggle == 0:
            if self.on:
                self.setImage(self.offImage)
                self.on = False
            else:
                self.setImage(self.onImage)
                self.on = True
        self.ticks += 1
