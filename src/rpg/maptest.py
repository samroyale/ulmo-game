#! /usr/bin/env python

import unittest
import pygame
import parser
import view

from pygame.locals import Rect

from view import TILE_SIZE

# initialize everything
pygame.init()
screen = pygame.display.set_mode((1, 1))

# this feels a bit hacky - is there a better way to do it?
parser.MAPS_FOLDER = "../maps"
parser.TILES_FOLDER = "../tiles"

rpgMap = parser.loadRpgMap("unit")

class MockSprite:

    def __init__(self, mapRect, level):
        self.mapRect = mapRect
        self.level = level
        self.upright = True
        
    def move(self, px, py):
        self.mapRect.move_ip(px, py)
        # pseudo z order that is used to test if one sprite is behind another
        self.z = int(self.mapRect.bottom + self.level * TILE_SIZE)
        

class GetMasksTest(unittest.TestCase):
    
    def testLevel1_span1(self):
        # horizontally spans only one tile                          
        rect = Rect(6 * TILE_SIZE + 2, 1 * TILE_SIZE - 24, 28, 48)
        spriteInfo = MockSprite(rect, 1)
        spriteInfo.move(0, 0)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(1, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(1, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))

    def testLevel1_span2(self):
        # horizontally spans two tiles                          
        rect = Rect(6 * TILE_SIZE + 18, 1 * TILE_SIZE - 24, 28, 48)
        spriteInfo = MockSprite(rect, 1)
        spriteInfo.move(0, 0)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(2, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(2, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        
    def testLevel2_span1(self):
        # horizontally spans only one tile                          
        rect = Rect(6 * TILE_SIZE + 2, 1 * TILE_SIZE - 24, 28, 48)
        spriteInfo = MockSprite(rect, 2)
        spriteInfo.move(0, 0)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))

    def testLevel2_span2(self):
        # horizontally spans two tiles                          
        rect = Rect(6 * TILE_SIZE + 18, 1 * TILE_SIZE - 24, 28, 48)
        spriteInfo = MockSprite(rect, 2)
        spriteInfo.move(0, 0)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))
        spriteInfo.move(0, TILE_SIZE)
        self.assertEqual(0, len(rpgMap.getMasks(spriteInfo)))

class MovementValidTest(unittest.TestCase):

    def testSpan1_1(self):
        # horizontally spans only one tile                          
        baseRect = Rect(5 * TILE_SIZE + 2, 2 * TILE_SIZE + 8, 28, 18)
        # [1,2] [S2]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [S2]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [S2] [S1.5]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [S1.5]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((True, 1.5), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((True, 1.5), rpgMap.isMoveValid(2, baseRect))
        # [S1.5] [S1.5]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((True, 1.5), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((True, 1.5), rpgMap.isMoveValid(2, baseRect))
        # [S1.5]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((True, 1.5), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((True, 1.5), rpgMap.isMoveValid(2, baseRect))
        # [S1.5] [S1]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [S1]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [S1] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getBaseRectTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))

    def testSpan2_1(self):
        # horizontally spans only one tile                          
        baseRect = Rect(5 * TILE_SIZE + 18, 2 * TILE_SIZE + 8, 28, 18)
        # [1,2] [1,2] [S2] [2]
        baseRect.move_ip(0, 16)
        self.assertEqual(4, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [S2] [2]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [S2] [2] [S1.5] [X]
        baseRect.move_ip(0, 16)
        self.assertEqual(4, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        self.assertEqual((True, 2, -1), rpgMap.isVerticalValid(1.5, baseRect))
        self.assertEqual((True, 2, -1), rpgMap.isVerticalValid(2, baseRect))
        self.assertEqual((True, 2, -1), rpgMap.isHorizontalValid(2, baseRect))
        # [S1.5] [X]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        self.assertEqual((True, 1.5, -1), rpgMap.isVerticalValid(1, baseRect))
        self.assertEqual((True, 1.5, -1), rpgMap.isVerticalValid(1.5, baseRect))
        self.assertEqual((False, 1.5, 0), rpgMap.isHorizontalValid(1.5, baseRect))
        # [S1.5] [X] [S1.5] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(4, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        self.assertEqual((True, 1.5, -1), rpgMap.isVerticalValid(1, baseRect))
        self.assertEqual((True, 1.5, -1), rpgMap.isVerticalValid(1.5, baseRect))
        self.assertEqual((False, 1.5, -1), rpgMap.isHorizontalValid(1.5, baseRect))
        # [S1.5] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        self.assertEqual((True, 1, 1), rpgMap.isVerticalValid(1, baseRect))
        self.assertEqual((True, 1.5, -1), rpgMap.isVerticalValid(1.5, baseRect))
        self.assertEqual((False, 1.5, 0), rpgMap.isHorizontalValid(1.5, baseRect))
        # [S1.5] [1] [S1] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(4, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        self.assertEqual((True, 1, 1), rpgMap.isVerticalValid(1, baseRect))
        self.assertEqual((True, 1, -1), rpgMap.isVerticalValid(1.5, baseRect))
        self.assertEqual((True, 1, 1), rpgMap.isHorizontalValid(1, baseRect))
        # [S1] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [S1] [1] [1] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(4, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 1.5), rpgMap.isMoveValid(1.5, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        
    def testSpan1_2(self):
        # horizontally spans only one tile                          
        baseRect = Rect(6 * TILE_SIZE + 2, 1 * TILE_SIZE + 8, 28, 18)
        # [1]
        baseRect.move_ip(0, 0)
        self.assertEqual(1, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1] [1,2]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1,2]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [1,2] [2]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [2]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [2] [X]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [X]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [X] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
    
    def testSpan2_2(self):
        # horizontally spans only one tile                          
        baseRect = Rect(6 * TILE_SIZE + 18, 1 * TILE_SIZE + 8, 28, 18)
        # [1] [1]
        baseRect.move_ip(0, 0)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1] [1] [1,2] [1,2]
        baseRect.move_ip(0, 16)
        self.assertEqual(4, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1,2] [1,2]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [1,2] [1,2] [2] [2]
        baseRect.move_ip(0, 16)
        self.assertEqual(4, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [2] [2]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((True, 2), rpgMap.isMoveValid(2, baseRect))
        # [2] [2] [X] [X]
        baseRect.move_ip(0, 16)
        self.assertEqual(4, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [X] [X]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [X] [X] [1] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(4, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))

    def testEmptyTile(self):
        baseRect = Rect(7 * TILE_SIZE + 2, 5 * TILE_SIZE + 8, 28, 18)
        # [1]
        baseRect.move_ip(0, 0)
        self.assertEqual(1, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual(True, all(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1] [ ]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual(True, all(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [ ]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual(True, all(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [ ] [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(2, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual(True, all(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((False, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        # [1]
        baseRect.move_ip(0, 16)
        self.assertEqual(1, len(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual(True, all(rpgMap.getSpanTiles(baseRect)))
        self.assertEqual((True, 1), rpgMap.isMoveValid(1, baseRect))
        self.assertEqual((False, 2), rpgMap.isMoveValid(2, baseRect))
        
if __name__ == "__main__":
    unittest.main()   
