#!/usr/bin/env python

class EventBus:
    
    def __init__(self):
        self.coinCollectedListeners = []
        self.keyCollectedListeners = []
        self.doorOpenedListeners = []
        self.checkpointReachedListeners = []
        self.doorOpeningListeners = []
        self.playerFootstepListeners = []
        self.mapTransitionListeners = []
        self.lifeLostListeners = []
        self.endGameListeners = []
        self.waspZoomingListeners = []
        self.waspHoveringListeners = []
        self.beetleCrawlingListeners = []
        self.playerFallingListeners = []
        self.bladesStabbingListeners = []
        self.boatStoppedListeners = []
        self.boatMovingListeners = []
        self.titleShownListeners = []
        self.gameStartedListeners = []
        
    def addCoinCollectedListener(self, coinCollectedListener):
        self.coinCollectedListeners.append(coinCollectedListener)
            
    def dispatchCoinCollectedEvent(self, coinCollectedEvent):
        for listener in self.coinCollectedListeners:
            listener.coinCollected(coinCollectedEvent)

    def addKeyCollectedListener(self, keyCollectedListener):
        self.keyCollectedListeners.append(keyCollectedListener)
            
    def dispatchKeyCollectedEvent(self, keyCollectedEvent):
        for listener in self.keyCollectedListeners:
            listener.keyCollected(keyCollectedEvent)

    def addDoorOpenedListener(self, doorOpenedListener):
        self.doorOpenedListeners.append(doorOpenedListener)
            
    def dispatchDoorOpenedEvent(self, doorOpenedEvent):
        for listener in self.doorOpenedListeners:
            listener.doorOpened(doorOpenedEvent)

    def addCheckpointReachedListener(self, checkpointReachedListener):
        self.checkpointReachedListeners.append(checkpointReachedListener)
            
    def dispatchCheckpointReachedEvent(self, checkpointReachedEvent):
        for listener in self.checkpointReachedListeners:
            listener.checkpointReached(checkpointReachedEvent)

    def addDoorOpeningListener(self, doorOpeningListener):
        self.doorOpeningListeners.append(doorOpeningListener)
        
    def dispatchDoorOpeningEvent(self, doorOpeningEvent):
        for listener in self.doorOpeningListeners:
            listener.doorOpening(doorOpeningEvent)

    def addPlayerFootstepListener(self, playerFootstepListener):
        self.playerFootstepListeners.append(playerFootstepListener)

    def dispatchPlayerFootstepEvent(self, playerFootstepEvent):
        for listener in self.playerFootstepListeners:
            listener.playerFootstep(playerFootstepEvent)

    def addMapTransitionListener(self, mapTransitionListener):
        self.mapTransitionListeners.append(mapTransitionListener)
        
    def dispatchMapTransitionEvent(self, mapTransitionEvent):
        for listener in self.mapTransitionListeners:
            listener.mapTransition(mapTransitionEvent)

    def addLifeLostListener(self, lifeLostListener):
        self.lifeLostListeners.append(lifeLostListener)
        
    def dispatchLifeLostEvent(self, lifeLostEvent):
        for listener in self.lifeLostListeners:
            listener.lifeLost(lifeLostEvent)

    def addEndGameListener(self, endGameListener):
        self.endGameListeners.append(endGameListener)
        
    def dispatchEndGameEvent(self, endGameEvent):
        for listener in self.endGameListeners:
            listener.endGame(endGameEvent)

    def addWaspZoomingListener(self, waspZoomingListener):
        self.waspZoomingListeners.append(waspZoomingListener)

    def dispatchWaspZoomingEvent(self, waspZoomingEvent):
        for listener in self.waspZoomingListeners:
            listener.waspZooming(waspZoomingEvent)

    def addBeetleCrawlingListener(self, beetleCrawlingListener):
        self.beetleCrawlingListeners.append(beetleCrawlingListener)

    def dispatchBeetleCrawlingEvent(self, beetleCrawlingEvent):
        for listener in self.beetleCrawlingListeners:
            listener.beetleCrawling(beetleCrawlingEvent)

    def addPlayerFallingListener(self, playerFallingListener):
        self.playerFallingListeners.append(playerFallingListener)

    def dispatchPlayerFallingEvent(self, playerFallingEvent):
        for listener in self.playerFallingListeners:
            listener.playerFalling(playerFallingEvent)
            
    def addBladesStabbingListener(self, bladesStabbingListener):
        self.bladesStabbingListeners.append(bladesStabbingListener)

    def dispatchBladesStabbingEvent(self, bladesStabbingEvent):
        for listener in self.bladesStabbingListeners:
            listener.bladesStabbing(bladesStabbingEvent)
            
    def addBoatStoppedListener(self, boatStoppedListener):
        self.boatStoppedListeners.append(boatStoppedListener)

    def dispatchBoatStoppedEvent(self, boatStoppedEvent):
        for listener in self.boatStoppedListeners:
            listener.boatStopped(boatStoppedEvent)

    def addBoatMovingListener(self, boatMovingListener):
        self.boatMovingListeners.append(boatMovingListener)

    def dispatchBoatMovingEvent(self, boatMovingEvent):
        for listener in self.boatMovingListeners:
            listener.boatMoving(boatMovingEvent)

    def addTitleShownListener(self, titleShownListener):
        self.titleShownListeners.append(titleShownListener)

    def dispatchTitleShownEvent(self, titleShownEvent):
        for listener in self.titleShownListeners:
            listener.titleShown(titleShownEvent)

    def addGameStartedListener(self, gameStartedListener):
        self.gameStartedListeners.append(gameStartedListener)

    def dispatchGameStartedEvent(self, gameStartedEvent):
        for listener in self.gameStartedListeners:
            listener.gameStarted(gameStartedEvent)
