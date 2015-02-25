#! /usr/bin/env python

import pygame

from othersprites import Beetle, Wasp, Blades, Boat
from staticsprites import Flames, Coin, Key, Chest, Rock, Door, Checkpoint

# map of sprite classes keyed on name, as they appear in the map files 
spriteClasses = {"flames": Flames,
                 "coin": Coin,
                 "key": Key,
                 "chest": Chest,
                 "rock": Rock,
                 "door": Door,
                 "checkpoint": Checkpoint,
                 "beetle": Beetle,
                 "wasp": Wasp,
                 "blades": Blades,
                 "boat": Boat}

"""
Returns a sprite instance based on the given mapSprite.  If the registry indicates
that the sprite has been removed from the map, this method returns None.  We also
apply any map actions at this point.
"""
def createSprite(mapSprite, rpgMap, eventBus, registry):
    tilePoints = mapSprite.tilePoints
    spriteMetadata = registry.getMetadata(mapSprite.uid);
    if spriteMetadata:
        # allow any interactions with the map, eg. an open door
        spriteMetadata.applyMapActions(rpgMap)
        # get tile points for later
        tilePoints = spriteMetadata.getTilePoints(tilePoints)
        if spriteMetadata.isRemovedFromMap():
            return None
    if mapSprite.type in spriteClasses:
        spriteClass = spriteClasses[mapSprite.type]
        sprite = spriteClass()
        sprite.setup(mapSprite.uid, rpgMap, eventBus)
        sprite.initMovement(mapSprite.level, tilePoints)
        return sprite
    print "sprite type not found:", mapSprite.type 
    return None

"""
Returns a sprite group for the given map.  This excludes any sprites that are
removed from the map.
"""
def createSpritesForMap(rpgMap, eventBus, registry):
    gameSprites = pygame.sprite.Group()
    if rpgMap.mapSprites:
        for mapSprite in rpgMap.mapSprites:
            sprite = createSprite(mapSprite, rpgMap, eventBus, registry)
            if sprite:
                gameSprites.add(sprite)
    return gameSprites
