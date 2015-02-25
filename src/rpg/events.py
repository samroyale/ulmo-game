#! /usr/bin/env python

"""
Simple events without metadata are typically used to play sound effects.
"""
class Event():    
    def getMetadata(self):
        pass

class DoorOpeningEvent(Event):
    pass

class PlayerFootstepEvent(Event):
    pass

class EndGameEvent(Event):
    pass

class WaspZoomingEvent(Event):
    pass

class BeetleCrawlingEvent(Event):
    pass

class PlayerFallingEvent(Event):
    pass

class BladesStabbingEvent(Event):
    pass

class BoatMovingEvent(Event):
    pass

class TitleShownEvent(Event):
    pass

class GameStartedEvent(Event):
    pass

"""
Defines an event that occurs when the player loses a life and is also used to
indicate game over.
"""
class LifeLostEvent(Event):
    def __init__(self, gameOver = False):
        self.gameOver = gameOver        

"""
Metadata events are used to pass metadata into the registry.  This is used to track
game state, eg. which items have been collected, which doors have been opened etc.
"""        
class MetadataEvent(Event):    
    def __init__(self, metadata):
        self.metadata = metadata
        
    def getMetadata(self):
        return self.metadata
        
class CoinCollectedEvent(MetadataEvent):
    def __init__(self, metadata):
        MetadataEvent.__init__(self, metadata)

class KeyCollectedEvent(MetadataEvent):
    def __init__(self, metadata):
        MetadataEvent.__init__(self, metadata)
        
class DoorOpenedEvent(MetadataEvent):
    def __init__(self, metadata):
        MetadataEvent.__init__(self, metadata)

class CheckpointReachedEvent(MetadataEvent):
    def __init__(self, metadata):
        MetadataEvent.__init__(self, metadata)

class BoatStoppedEvent(MetadataEvent):
    def __init__(self, metadata):
        MetadataEvent.__init__(self, metadata)
                
"""
Metadata is collated in the registry and is used to track game state, eg. which items
have been collected, which doors have been opened etc. When sprites are created for a
given map we also apply any map actions - see spritebuilder for more details.
"""
class SpriteMetadata:    
    def __init__(self, uid):
        self.uid = uid
    
    def isRemovedFromMap(self):
        return True
    
    def applyMapActions(self, rpgMap):
        pass
    
    def getTilePoints(self, tilePoints):
        return tilePoints
    
class CoinMetadata(SpriteMetadata):    
    def __init__(self, uid):
        SpriteMetadata.__init__(self, uid)
        
class KeyMetadata(SpriteMetadata):
    def __init__(self, uid):
        SpriteMetadata.__init__(self, uid)

class DoorMetadata(SpriteMetadata):    
    def __init__(self, uid, tilePosition, level):
        SpriteMetadata.__init__(self, uid)
        self.x, self.y = tilePosition[0], tilePosition[1]
        self.level = level

    # makes the corresponding tile available for this level
    def applyMapActions(self, rpgMap):
        rpgMap.addLevel(self.x, self.y, self.level)

class CheckpointMetadata(SpriteMetadata):    
    def __init__(self, uid, mapName, tilePosition, level, coinCount, keyCount):
        SpriteMetadata.__init__(self, uid)
        self.mapName = mapName
        self.tilePosition = tilePosition
        self.level = level
        self.coinCount = coinCount
        self.keyCount = keyCount
        
class BoatMetadata(SpriteMetadata):
    def __init__(self, uid, tilePosition):
        SpriteMetadata.__init__(self, uid)
        self.endPosition = tilePosition

    def getTilePoints(self, tilePoints):
        return [self.endPosition]
    
    def isRemovedFromMap(self):
        return False

