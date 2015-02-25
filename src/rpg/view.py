#!/usr/bin/env python

import os, pygame

from pygame.transform import scale
from pygame.locals import RLEACCEL

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

SCALAR = 2

TILE_SIZE = 16 * SCALAR

VIEW_WIDTH = TILE_SIZE * 16
VIEW_HEIGHT = TILE_SIZE * 10

TRANSPARENT_COLOUR = GREEN

NONE, UP, DOWN, LEFT, RIGHT = 0, 1, 2, 4, 8

DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

def createRectangle(dimensions, colour = None):
    rectangle = pygame.Surface(dimensions).convert()
    if colour is not None:
        rectangle.fill(colour)
    return rectangle

def loadImage(imagePath, colourKey = None):
    try:
        image = pygame.image.load(imagePath)
    except pygame.error, message:
        print "Cannot load image: ", os.path.abspath(imagePath)
        raise SystemExit, message
    image = image.convert()
    if colourKey is not None:
        image.set_colorkey(colourKey, RLEACCEL)
    return image

def loadScaledImage(imagePath, colourKey = None, scalar = SCALAR):
    img = loadImage(imagePath, colourKey)
    return scale(img, (img.get_width() * scalar, img.get_height() * scalar))
        
def createDuplicateSpriteImage(spriteImage):
    # transparency is set on the duplicate - this allows us to draw over
    # the duplicate image with areas that are actually transparent
    img = createRectangle((spriteImage.get_width(), spriteImage.get_height()))
    img.blit(spriteImage, (0, 0))
    img.set_colorkey(TRANSPARENT_COLOUR, RLEACCEL)
    return img

# process animation frames from the composite image
def processMovementFrames(framesImage, numFrames = 4):
    # work out width + height
    framesRect = framesImage.get_rect()
    width = framesRect.width // numFrames
    height = framesRect.height // len(DIRECTIONS)
    # map of image lists for animation keyed on direction
    animationFrames = {}
    row = 0
    for direction in DIRECTIONS:
        frames = []
        rowOffsetY = row * height
        for i in range(numFrames):
            img = framesImage.subsurface(i * width, rowOffsetY, width, height)
            frames.append(img)
        animationFrames[direction] = frames
        row += 1
    return animationFrames

# create a copy of the given animation frames
def copyMovementFrames(animationFrames):
    # map of image lists for animation keyed on direction
    animationFramesCopy = {}
    for direction in DIRECTIONS:
        framesCopy = []
        for frame in animationFrames[direction]:
            img = createDuplicateSpriteImage(frame)
            framesCopy.append(img)
        animationFramesCopy[direction] = framesCopy
    return animationFramesCopy

# process animation frames from the composite image
def processStaticFrames(framesImage, numFrames = 4):
    framesRect = framesImage.get_rect()
    width = framesRect.width // numFrames
    height = framesRect.height
    # map of images for animation
    animationFrames = []
    for i in range(numFrames):
        img = framesImage.subsurface((i * width, 0), (width, height))
        animationFrames.append(img)
    return animationFrames

# create a copy of the given animation frames
def copyStaticFrames(animationFrames):
    # map of image lists for animation keyed on direction
    animationFramesCopy = []
    for frame in animationFrames:
        img = createDuplicateSpriteImage(frame)
        animationFramesCopy.append(img)
    return animationFramesCopy

def createTransparentRect(dimensions):
    transparentRect = createRectangle(dimensions, TRANSPARENT_COLOUR)
    transparentRect.set_colorkey(TRANSPARENT_COLOUR, RLEACCEL)
    return transparentRect

def processFontImage(fontImage, charWidth, rows = 1):
    charImages = []
    charHeight = fontImage.get_height() // rows
    for i in range(rows):
        x, y = 0, i * charHeight
        while x < fontImage.get_width():
            charImage = fontImage.subsurface((x, y), (charWidth, charHeight))
            charImages.append(charImage)
            x += charWidth
    return charImages
