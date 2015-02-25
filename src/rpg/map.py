#! /usr/bin/env python

from __future__ import with_statement

import math
import view
import mapevents

from view import TILE_SIZE

MIN_SHUFFLE = (0, -1, -1, 1)
MAX_SHUFFLE = (-1, 1, 0, -1)

"""
Encapsulates the logic required for the main map.  You should not instantiate
this class directly - instead, use parser.loadRpgMap and the mapTiles, mapSprites
and mapEvents will be populated from the named map file.
"""
class RpgMap:
    
    def __init__(self, name, music, mapTiles, mapSprites, mapEvents):
        self.name = name
        self.music = music
        self.mapTiles = mapTiles
        self.cols = len(mapTiles)
        self.rows = len(mapTiles[0])
        self.mapSprites = mapSprites
        self.initialiseMapImage()
        self.initialiseEvents(mapEvents)
        self.toRestore = None
        
    def initialiseMapImage(self):
        self.mapImage = view.createRectangle((self.cols * TILE_SIZE, self.rows * TILE_SIZE),
                                              view.BLACK)
        for tiles in self.mapTiles:
            for tile in tiles:
                tileImage = tile.createTileImage()
                if tileImage:
                    self.mapImage.blit(tileImage, (tile.x * TILE_SIZE, tile.y * TILE_SIZE))
        self.mapRect = self.mapImage.get_rect()
    
    def initialiseEvents(self, mapEvents):
        self.boundaryEvents = {}
        self.tileEvents = {}
        for event in mapEvents:
            if event.type == mapevents.TILE_EVENT:
                self.mapTiles[event.x][event.y].addEvent(event)
            elif event.type == mapevents.BOUNDARY_EVENT:
                if event.boundary in self.boundaryEvents:
                    self.boundaryEvents[event.boundary].append(event)
                else:
                    self.boundaryEvents[event.boundary] = [event]
    
    """
    The map restricts movement via the following system:

    Each tile has 0 or more levels that determine if a sprite can move onto them.
    At its most basic, if the sprite is at level 1 they will be blocked if they
    attempt to move onto a level 2 tile. However, things get more interesting if
    steps are involved. For example, consider the following representation of a
    two-level map with steps linking the two levels:
    
    [2]  [S2]  [2]  <- level 2
    [X] [S1.5] [X]  <- top of steps + wall on either side
    [1] [S1.5] [1]  <- bottom of steps + level 1 on either side
    [1]  [S1]  [1]  <- level 1
    
    Note that [X] represents a tile that is inaccessible, [1] and [2] are level 1
    and 2 tiles and [S*] are 'specials'.  All this information can be viewed/edited
    using the map editor.
    
    Movement is deemed to be valid if one of the following criteria is met - the
    phrase 'base tiles' is used here to mean all tiles that are touched by the base
    rect of the sprite:
    
    > All base tiles are at the same level as the sprite. Eg. [1] [1] would be ok,
      [1] [S1] would be ok, [1] [S1.5] would not.
        
    > All base tiles are 'specials' and the difference between the min and max
      level is less than one. In addition, the difference between all tile
      levels and the sprite level must also be less than one. Eg. [S1] [S1.5]
      would be ok, [S1.5] [S2] would be ok, [S1] [S2] would not.
    
    Note that base tiles can include anything from 1 to 4 tiles - I just used
    two-tile examples above for the sake of brevity.
    
    If movement is valid, the sprite level is made equal to the maximum tile level
    of the base tiles. This allows the sprite to move between one level and another.
    """
    def isSpanValid(self, level, spanTiles):
        sameLevelCount = 0
        specialLevels = []
        # iterate through base tiles and gather information
        for tile in spanTiles:
            increment, specialLevel = tile.testValidity(level)
            sameLevelCount += increment
            if specialLevel:
                specialLevels.append(specialLevel)
        # test validity of the requested movement
        spanTileCount = len(spanTiles)
        if sameLevelCount == spanTileCount:
            return True, level
        elif len(specialLevels) == spanTileCount:
            minLevel = min(specialLevels)
            maxLevel = max(specialLevels)
            if maxLevel - minLevel < 1:
                # ensure we return a whole number if possible
                retLevel = maxLevel if int(maxLevel) == maxLevel else minLevel 
                return True, retLevel
        return False, level
    
    def isMoveValid(self, level, baseRect):
        return self.isSpanValid(level, self.getBaseRectTiles(baseRect))
    
    def isStripeValid(self, level, stripes, min, max):
        if len(stripes) < 2:
            return False, level, 0
        sortedKeys = sorted(stripes.keys())
        minDiff = abs(sortedKeys[0] * TILE_SIZE - min)
        maxDiff = abs((sortedKeys[-1] + 1) * TILE_SIZE - max)
        if minDiff < maxDiff:
            return self.isShuffleValid(stripes, sortedKeys, level, MIN_SHUFFLE)
        return self.isShuffleValid(stripes, sortedKeys, level, MAX_SHUFFLE)
        
    def isShuffleValid(self, stripes, sortedKeys, level, shuffle):
        index1, shuffle1, index2, shuffle2 = shuffle
        stripe = stripes[sortedKeys[index1]]
        valid, level = self.isSpanValid(level, stripe)
        if valid:
            return valid, level, shuffle1
        stripe = stripes[sortedKeys[index2]]
        valid, level = self.isSpanValid(level, stripe)
        return valid, level, shuffle2
                
    def isVerticalValid(self, level, baseRect):
        return self.isStripeValid(level, self.verticals,
                                  baseRect.left, baseRect.right)

    def isHorizontalValid(self, level, baseRect):
        return self.isStripeValid(level, self.horizontals,
                                  baseRect.top, baseRect.bottom)
        
    """
    The given sprite must contain mapRect, level, z and upright attributes.  Typically
    this object will be a real sprite, but for ease of unit testing it can be anything.
    """
    def getMasks(self, sprite):
        spriteTiles = self.getSpanTiles(sprite.mapRect)
        masks = {}
        for tile in spriteTiles:
            if tile:
                tileMasks = tile.getMasks(sprite.level, sprite.z, sprite.upright)
                if tileMasks:
                    masks[(tile.x, tile.y)] = tileMasks
        return masks
    
    """
    Returns all the tiles that are touched by the given rectangle.
    """
    def getSpanTiles(self, rect):
        rectTiles = []
        x1, y1 = self.convertTopLeft(rect.left, rect.top)
        x2, y2 = self.convertBottomRight(rect.right - 1, rect.bottom - 1)
        for x in range(x1, x2 + 1):
            rectTiles += self.mapTiles[x][y1:y2 + 1]
        return rectTiles
    
    """
    Returns all the tiles that are touched by the given rectangle.  As a side-effect,
    this method also caches the 'verticals' + 'horizontals' - the same tiles, but
    divided into columns + rows.  This makes it much easier to check for valid shuffles
    if the requested movement is invalid.
    """
    def getBaseRectTiles(self, rect):
        rectTiles = []
        x1, y1 = self.convertTopLeft(rect.left, rect.top)
        x2, y2 = self.convertBottomRight(rect.right - 1, rect.bottom - 1)
        self.verticals = {}
        for x in range(x1, x2 + 1):
            self.verticals[x] = self.mapTiles[x][y1:y2 + 1]
            rectTiles += self.verticals[x]
        self.horizontals = {}
        for y in range(y1, y2 + 1):
            self.horizontals[y] = [self.mapTiles[x][y] for x in range(x1, x2 + 1)]
        return rectTiles
    
    """
    Returns the boundary event for the given boundary + tile range. Returns
    None if no such event exists.
    """    
    def getBoundaryEvent(self, boundary, tileRange):
        if boundary in self.boundaryEvents:
            for event in self.boundaryEvents[boundary]:
                testList = [i in event.range for i in tileRange]
                if all(testList):
                    return event
        return None
    
    """
    Returns a tile event or falling event. Returns None if such an event has not
    been triggered.
    """
    def getActionEvent(self, level, baseRect):
        downLevels = []
        spanTiles = self.getSpanTiles(baseRect)
        for tile in spanTiles:
            event = tile.getEvent(level)
            if event:
                return event
            downLevel = tile.getDownLevel(level)
            if downLevel:
                downLevels.append(downLevel)
        # a falling event is returned only if all the span tiles have a down level
        if downLevels and len(downLevels) == len(spanTiles):
            return mapevents.FallingEvent(downLevels[0])
        return None
            
    def convertTopLeft(self, px, py):
        return max(0, px // TILE_SIZE), max(0, py // TILE_SIZE)
        
    def convertBottomRight(self, px, py):
        return min(self.cols - 1, px // TILE_SIZE), min(self.rows - 1, py // TILE_SIZE)
    
    """
    Adds a new level to the specified tile and stores it for restoration.
    """
    def addLevel(self, x, y, level):
        if self.toRestore == None:
            self.toRestore = set()
        self.toRestore.add(self.mapTiles[x][y].addNewLevel(level))
    
    """
    Restores any modified tiles to their original state.
    """    
    def restore(self):
        if self.toRestore == None:
            return self
        for tile in self.toRestore:
            tile.restore()
        self.toRestore = None
        return self

"""
A repository of named tile images.  Instances of this class are created and used
whenever a new map is loaded from disk.
"""
class TileSet:
    
    def __init__(self, tiles):
        self.tiles = tiles

    def getTile(self, name):
        if name in self.tiles:
            return self.tiles[name]
        return None
    
"""
Represents a single tile on an RpgMap.
"""
class MapTile:
    
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.levels = []
        self.tiles = []
        self.originalLevels = None
        self.specialLevels = None
        self.downLevels = None
        self.masks = None
        self.events = None
        
    def addLevel(self, level):
        self.levels.append(level)
    
    """
    If we add a new level (eg. when the player opens a door) we need to restore
    the map to its original state when we next pull it from the cache - hence we
    store the original levels before adding to them.
    """    
    def addNewLevel(self, level):
        if self.originalLevels == None:
            self.originalLevels = [l for l in self.levels]
        self.addLevel(level)
        return self
        
    def restore(self):
        if self.originalLevels == None:
            return
        self.levels = self.originalLevels
        self.originalLevels = None		
        
    def addTile(self, tile):
        self.tiles.append(tile)
        
    def addSpecialLevel(self, level):
        if not self.specialLevels:
            self.specialLevels = {}
        if int(level) == level:
            self.specialLevels[level] = level
        else:
            self.specialLevels[math.floor(level)] = level
            self.specialLevels[math.ceil(level)] = level
    
    def addDownLevel(self, level, downLevel):
        # print "DOWN: %s %s" % (level, downLevel)
        if not self.downLevels:
            self.downLevels = {}
        self.downLevels[level] = downLevel
           
    def addMask(self, tileIndex, level, flat = True):
        if not self.masks:
            self.masks = []
        self.masks.append(MaskInfo(tileIndex, level, flat, self.y))
        
    def addEvent(self, event):
        if not self.events:
            self.events = []
        self.events.append(event)
            
    def createTileImage(self):
        if len(self.tiles) == 0:
            return None
        elif len(self.tiles) > 1:
            # if we're layering more than one image we don't want to draw on any of
            # the original images because that will affect every copy
            tileImage = view.createRectangle((TILE_SIZE, TILE_SIZE), view.BLACK)
            for image in self.tiles:
                tileImage.blit(image, (0, 0))
            return tileImage
        return self.tiles[0]
    
    def testValidity(self, level):
        if level in self.levels:
            return 1, None
        downLevel = self.getDownLevel(level)
        if downLevel:
            return 1, None
        specialLevel = self.getSpecialLevel(level)
        if specialLevel:
            if specialLevel == level:
                return 1, specialLevel
            return 0, specialLevel
        return 0, None
    
    def getSpecialLevel(self, level):
        if not self.specialLevels:
            return None
        if level in self.specialLevels:
            return self.specialLevels[level]
        key = math.floor(level)
        if key in self.specialLevels:
            return self.specialLevels[key]
        key = math.ceil(level)
        if key in self.specialLevels:
            return self.specialLevels[key]
        return None
    
    def getDownLevel(self, level):
        if not self.downLevels:
            return None
        if level in self.downLevels:
            return self.downLevels[level]
    
    def getEvent(self, level):
        if not self.events:
            return None
        for event in self.events:
            if event.level == level:
                return event
        return None
    
    def getMasks(self, spriteLevel, spriteZ, spriteUpright):
        if not self.masks:
            return None
        masks = []
        for maskInfo in self.masks:
            if maskInfo.z > spriteZ:
                if maskInfo.flat and maskInfo.level == spriteLevel:
                    continue
                masks.append(self.tiles[maskInfo.tileIndex])
            else:
                if spriteUpright or maskInfo.flat or maskInfo.level < spriteLevel:
                    continue
                masks.append(self.tiles[maskInfo.tileIndex])
        if len(masks) > 0:
            return masks
        return None
        
    def __str__(self):
        result = "<MapTile:\
         [" + str(self.x) + "," + str(self.y) + "]\
 tiles=" + str(len(self.tiles)) + "\
 levels=" + str(self.levels) + "\
 specialLevels=" + str(self.specialLevels) + "\
 masks=" + str(self.masks) + "\
 events=" + str(self.events) + "\>"
        return result

"""
Encapsulates information required for masking. 
"""
class MaskInfo:
    def __init__(self, tileIndex, level, flat, y):
        self.level = level
        self.flat = flat
        self.tileIndex = tileIndex
        self.z = (y + 1) * TILE_SIZE + level * TILE_SIZE - 1

"""
Sprite placeholder that is later used to construct a real sprite.
"""        
class MapSprite:
    def __init__(self, type, uid, level, tilePoints):
        self.type = type
        self.uid = uid
        self.level = level
        self.tilePoints = tilePoints
            
