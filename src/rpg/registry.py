#! /usr/bin/env python

class RegistryHandler:
    
    def setRegistry(self, registry):
        self.registry = registry
        self.snapshot = registry.takeSnapshot()
        
    def switchToSnapshot(self):
        self.setRegistry(self.snapshot)

    def registerMetadata(self, spriteMetadata):
        self.registry.registerMetadata(spriteMetadata)
        
    def getMetadata(self, uid):
        return self.registry.getMetadata(uid)
    
    def coinCollected(self, coinCollectedEvent):
        self.registry.coinCollected(coinCollectedEvent)
        
    def keyCollected(self, keyCollectedEvent):
        self.registry.keyCollected(keyCollectedEvent)
    
    def keyUsed(self, keyUsedEvent):
        self.registry.keyUsed(keyUsedEvent)
            
    def doorOpened(self, doorOpenedEvent):
        self.registry.doorOpened(doorOpenedEvent)
        
    def boatStopped(self, boatStoppedEvent):
        self.registry.boatStopped(boatStoppedEvent)
        
    def checkpointReached(self, checkpointReachedEvent):
        self.snapshot = self.registry.checkpointReached(checkpointReachedEvent)
        
    def getPlayerPosition(self):
        return self.registry.playerPosition
        
    def setPlayerPosition(self, playerPosition):
        self.registry.playerPosition = playerPosition
        
    def takeSnapshot(self):
        self.snapshot = self.registry.takeSnapshot()
                            
"""
Registry class that stores the state of the game.  A save game feature could be
implemented by serializing this class.
"""
class Registry:
    
    def __init__(self, mapName, playerPosition, playerLevel,
                 coinCount = 0, keyCount = 0, spriteMetadata = None, checkpoint = None):
        self.mapName = mapName
        self.playerPosition = playerPosition
        self.playerLevel = playerLevel
        # a map of sprite metadata keyed on uid
        self.spriteMetadata = spriteMetadata
        if self.spriteMetadata is None: 
            self.spriteMetadata = {}
        # counts
        self.coinCount = coinCount
        self.keyCount = keyCount
        # metadata for the last checkpoint reached
        self.checkpoint = checkpoint

    def registerMetadata(self, spriteMetadata):
        self.spriteMetadata[spriteMetadata.uid] = spriteMetadata
        
    def getMetadata(self, uid):
        if self.checkpoint and self.checkpoint.uid == uid:
            myCheckpoint = self.checkpoint
            self.checkpoint = None
            return myCheckpoint
        if uid in self.spriteMetadata:
            return self.spriteMetadata[uid]
        return None
    
    def copyMetadata(self):
        return dict((uid, self.spriteMetadata[uid]) for uid in self.spriteMetadata)
            
    def takeSnapshot(self):
        return Registry(self.mapName,
                        self.playerPosition,
                        self.playerLevel,
                        self.coinCount,
                        self.keyCount,
                        self.copyMetadata(),
                        self.checkpoint)
                
    # ==========================================================================
         
    def coinCollected(self, coinCollectedEvent):
        self.registerMetadata(coinCollectedEvent.getMetadata())
        
    def keyCollected(self, keyCollectedEvent):
        self.registerMetadata(keyCollectedEvent.getMetadata())
    
    def doorOpened(self, doorOpenedEvent):
        self.registerMetadata(doorOpenedEvent.getMetadata())
        
    def boatStopped(self, boatStoppedEvent):
        self.registerMetadata(boatStoppedEvent.getMetadata())
        
    def checkpointReached(self, checkpointReachedEvent):
        checkpoint = checkpointReachedEvent.getMetadata()
        print "checkpoint reached: %s" % checkpoint.uid
        return Registry(checkpoint.mapName,
                        checkpoint.tilePosition,
                        checkpoint.level,
                        checkpoint.coinCount,
                        checkpoint.keyCount,
                        self.copyMetadata(),
                        checkpoint)
        