#! /usr/bin/env python

import os
import view

from view import SCALAR

FONT_FOLDER = "images"

CHARS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
         'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '.', '!',
         '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '/', ' ']

NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

"""
Font class that maps a list of supported chars to their corresponding images.
This is then used to get an image for a given piece of text.
"""
class Font:
    
    def __init__(self, supportedChars, charImages):
        self.chars = {}
        for i, char in enumerate(supportedChars):
            self.chars[char] = charImages[i]
        self.charWidth = charImages[0].get_width()
        self.charHeight = charImages[0].get_height()
            
    def getTextImage(self, text):
        # filter out any unsupported chars
        supportedText = [c for c in text if c in self.chars]
        textImage = view.createTransparentRect((len(supportedText) * self.charWidth, self.charHeight))
        for i, char in enumerate(supportedText):
            textImage.blit(self.chars[char], (i * self.charWidth, 0))
        return textImage
            
class GameFont(Font):

    fontImage = None
    
    def __init__(self):
        if GameFont.fontImage is None:    
            imagePath = os.path.join(FONT_FOLDER, "font-white.png")
            GameFont.fontImage = view.loadScaledImage(imagePath)        
        charImages = view.processFontImage(GameFont.fontImage, 8 * SCALAR, 3)
        Font.__init__(self, CHARS, charImages)
        
class TitleFont(Font):

    fontImage = None
    
    def __init__(self):
        if TitleFont.fontImage is None:    
            imagePath = os.path.join(FONT_FOLDER, "font-black.png")
            TitleFont.fontImage = view.loadScaledImage(imagePath)        
        charImages = view.processFontImage(TitleFont.fontImage, 8 * SCALAR, 3)
        Font.__init__(self, CHARS, charImages)
        
class NumbersFont(Font):

    fontImage = None
    
    def __init__(self):
        if NumbersFont.fontImage is None:    
            imagePath = os.path.join(FONT_FOLDER, "numbers.png")
            NumbersFont.fontImage = view.loadScaledImage(imagePath)        
        charImages = view.processFontImage(NumbersFont.fontImage, 8 * SCALAR)
        Font.__init__(self, NUMBERS, charImages)