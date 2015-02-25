#! /usr/bin/env python

from __future__ import with_statement

import os
import view
import map

from pygame.locals import Rect

from mapevents import BoundaryEvent, TileEvent, BoundaryTransition, SceneTransition, EndGameTransition
from view import UP, DOWN, LEFT, RIGHT

TILES_FOLDER = "tiles"
MAPS_FOLDER = "maps"
#MAPS_FOLDER = "maps093"
OPEN_SQ_BRACKET = "["
CLOSE_SQ_BRACKET = "]"
SPECIAL_LEVEL = "S"
DOWN_LEVEL = "D"
VERTICAL_MASK = "V"
COLON = ":"
COMMA = ","
SPRITE = "sprite"
EVENT = "event"
MUSIC = "music"
DASH = "-"

BOUNDARIES = {"up": UP, "down": DOWN, "left": LEFT, "right": RIGHT}

mapCache = {}

def getXY(xyStr, delimiter = COMMA):
    return [int(n) for n in xyStr.split(delimiter)]

def getTilePoints(xyList, delimiter = COMMA):
    tilePoints = []
    for xy in xyList:
        tilePoints.append(getXY(xy, delimiter))
    return tilePoints
    
def loadRpgMap(name):
    # check cache first
    if name in mapCache:
        return mapCache[name].restore()
    # tileData is keyed on an x,y tuple
    tileData = {}
    spriteData = []
    eventData = []
    music = None
    # parse map file - each line represents one map tile        
    mapPath = os.path.join(MAPS_FOLDER, name + ".map")
    print "loading: %s" % mapPath
    with open(mapPath) as mapFile:
        # eg. 10,4 [1] water:dark grass:l2 wood:lrs_supp:3
        maxX, maxY = 0, 0
        for line in mapFile:
            try:
                line = line.strip()
                if len(line) > 0:                        
                    bits = line.split()
                    if len(bits) > 0:
                        if bits[0] == SPRITE:
                            if len(bits) > 1:
                                spriteData.append(bits[1:])
                        elif bits[0] == EVENT:
                            if len(bits) > 1:
                                eventData.append(bits[1:])
                        elif bits[0] == MUSIC:
                            if len(bits) > 1:
                                music = bits[1]
                        else:                          
                            tilePoint = bits[0]
                            #print "%s -> %s" % (tileRef, tileName)
                            x, y = getXY(tilePoint)
                            maxX, maxY = max(x, maxX), max(y, maxY)
                            if len(bits) > 1:
                                tileData[(x, y)] = bits[1:]
            except ValueError:
                pass
    # create map tiles, sprites, events + music
    mapTiles = createMapTiles(maxX + 1, maxY + 1, tileData)
    mapSprites = createMapSprites(spriteData, name)
    mapEvents = createMapEvents(eventData)
    # create map and return
    myMap = map.RpgMap(name, music, mapTiles, mapSprites, mapEvents)
    mapCache[name] = myMap
    return myMap

def createMapTiles(cols, rows, tileData):
    # create the map tiles
    mapTiles = [[map.MapTile(x, y) for y in range(rows)] for x in range(cols)]
    # iterate through the tile data and set the map tiles
    tileSets = {}     
    for tilePoint in tileData.keys():
        bits = tileData[tilePoint]
        x, y = tilePoint[0], tilePoint[1]
        mapTile = mapTiles[x][y]
        # print bits
        startIndex = 0
        if bits[0][0] == OPEN_SQ_BRACKET and bits[0][-1] == CLOSE_SQ_BRACKET:
            # levels
            startIndex = 1
            levels = bits[0][1:-1].split(COMMA)
            for level in levels:
                if level[0] == SPECIAL_LEVEL:
                    mapTile.addSpecialLevel(float(level[1:]))
                elif level[0] == DOWN_LEVEL:
                    levelBits = level[1:].split(DASH)
                    mapTile.addDownLevel(int(levelBits[0]), int(levelBits[1]))
                else:
                    mapTile.addLevel(int(level))
        # tiles images
        for tileIndex, tiles in enumerate(bits[startIndex:]):
            tileBits = tiles.split(COLON)
            if len(tileBits) > 1:
                tileSetName = tileBits[0]
                if tileSetName in tileSets:
                    tileSet = tileSets[tileSetName]
                else:
                    tileSet = loadTileSet(tileSetName)
                    tileSets[tileSetName] = tileSet
                tileName = tileBits[1]
                mapTile.addTile(tileSet.getTile(tileName))
                # masks
                if len(tileBits) > 2:
                    maskLevel = tileBits[2]
                    # mapTile.addMaskTile(maskLevel, tileSet.getTile(tileName))
                    if maskLevel[0] == VERTICAL_MASK:
                        mapTile.addMask(tileIndex, int(maskLevel[1:]), False)
                    else:    
                        mapTile.addMask(tileIndex, int(maskLevel))
    return mapTiles

def loadTileSet(name):
    # print "load tileset: %s" % (name)
    # tileSet = map.TileSet()
    tiles = {}
    # load tile set image
    imagePath = os.path.join(TILES_FOLDER, name + ".png")
    tilesImage = view.loadScaledImage(imagePath, view.TRANSPARENT_COLOUR)
    # parse metadata - each line represents one tile in the tile set
    metadataPath = os.path.join(TILES_FOLDER, name + "_metadata.txt")
    with open(metadataPath) as metadata:
        # eg. 1,5 lst1
        for line in metadata:
            try:
                line = line.strip()
                if len(line) > 0:                        
                    tilePoint, tileName = line.strip().split()
                    # print "%s -> %s" % (tileRef, tileName)
                    x, y = tilePoint.split(COMMA)
                    px, py = int(x) * view.TILE_SIZE, int(y) * view.TILE_SIZE
                    tileRect = Rect(px, py, view.TILE_SIZE, view.TILE_SIZE)
                    tileImage = tilesImage.subsurface(tileRect).copy()
                    tiles[tileName] = tileImage
                    # self.maskTiles[tileName] = view.createMaskTile(tileImage)
            except ValueError:
                pass
    # create tile set and return
    return map.TileSet(tiles)

def createMapSprites(spriteData, mapName):
    mapSprites = []
    typeCounts = {}
    for spriteBits in spriteData:
        if len(spriteBits) > 2:
            # create unique ID for this sprite
            type = spriteBits[0]
            if type in typeCounts:
                typeCounts[type] += 1
            else:
                typeCounts[type] = 0
            typeCount = typeCounts[type]
            uid = mapName + COLON + type + COLON + str(typeCount)
            # extract movement info
            level = int(spriteBits[1])
            tilePoints = getTilePoints(spriteBits[2:])
            mapSprite = map.MapSprite(type, uid, level, tilePoints)
            mapSprites.append(mapSprite)
    return mapSprites
            
def createMapEvents(eventData):
    mapEvents = []
    for eventDataBits in eventData:
        eventBits = None
        transitionBits = None
        try:
            eventIndex = eventDataBits.index(COLON)
            eventBits = eventDataBits[0:eventIndex]
            transitionBits = eventDataBits[eventIndex + 1:]
        except (ValueError, IndexError):
            pass
        if transitionBits:
            transition = None
            transitionType = transitionBits[0]
            if transitionType == "boundary":
                transition = createBoundaryTransition(transitionBits)
            elif transitionType == "transition":
                transition = createSceneTransition(transitionBits)
            elif transitionType == "end":
                transition = createEndTransition()
            if transition and eventBits:
                event = None
                eventType = eventBits[0]
                if eventType == "boundary":
                    event = createBoundaryEvent(eventBits, transition)
                elif eventType == "tile":
                    event = createTileEvent(eventBits, transition)
                if event:
                    mapEvents.append(event)
    return mapEvents
                            
def createBoundaryTransition(transitionBits):
    if len(transitionBits) < 3:
        return None
    mapName = transitionBits[1]
    boundary = BOUNDARIES[transitionBits[2]]
    if len(transitionBits) > 3:
        modifier = int(transitionBits[3])
        return BoundaryTransition(mapName, boundary, modifier)
    return BoundaryTransition(mapName, boundary)

def createSceneTransition(transitionBits):
    if len(transitionBits) < 5:
        return None
    mapName = transitionBits[1]
    x, y = getXY(transitionBits[2])
    level = int(transitionBits[3])
    direction = BOUNDARIES[transitionBits[4]]
    if len(transitionBits) > 5:
        boundary = BOUNDARIES[transitionBits[5]]
        return SceneTransition(mapName, x, y, level, direction, boundary)
    return SceneTransition(mapName, x, y, level, direction)

def createEndTransition():
    return EndGameTransition()
    
def createBoundaryEvent(eventBits, transition):
    if len(eventBits) < 3:
        return None
    boundary = BOUNDARIES[eventBits[1]]
    range = eventBits[2]
    if DASH in range:
        min, max = getXY(range, DASH)
        return BoundaryEvent(transition, boundary, min, max)
    return BoundaryEvent(transition, boundary, int(range))

def createTileEvent(eventBits, transition):
    if len(eventBits) < 3:
        return None
    x, y = getXY(eventBits[1])
    level = int(eventBits[2])
    return TileEvent(transition, x, y, level)
