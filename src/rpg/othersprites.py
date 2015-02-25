#!/usr/bin/env python

from sprites import *
from spriteframes import StaticFrames, DirectionalFrames, DIRECTION
from view import UP, DOWN, LEFT, RIGHT, VIEW_WIDTH, VIEW_HEIGHT
from events import WaspZoomingEvent, BeetleCrawlingEvent, BladesStabbingEvent, BoatMovingEvent, BoatStoppedEvent, BoatMetadata

"""
Metadata is used to provide a loose coupling between the sprite movement and
the sprite frames.  Anything the sprite frames might be interested in, eg. the
direction, can be passed through.
""" 
UP_METADATA = {DIRECTION: UP}
DOWN_METADATA = {DIRECTION: DOWN}
LEFT_METADATA = {DIRECTION: LEFT}
RIGHT_METADATA = {DIRECTION: RIGHT}

MOVEMENT = {UP: (0, -MOVE_UNIT, UP_METADATA),
            DOWN: (0, MOVE_UNIT, DOWN_METADATA),
            LEFT: (-MOVE_UNIT, 0, LEFT_METADATA),
            RIGHT: (MOVE_UNIT, 0, RIGHT_METADATA)}

ZOOM_MOVEMENT = {UP: (0, -2 * MOVE_UNIT, UP_METADATA),
                 DOWN: (0, 2 * MOVE_UNIT, DOWN_METADATA),
                 LEFT: (-2 * MOVE_UNIT, 0, LEFT_METADATA),
                 RIGHT: (2 * MOVE_UNIT, 0, RIGHT_METADATA)}

BEETLE_FRAME_SKIP = 12 // VELOCITY
WASP_FRAME_SKIP = 4 // VELOCITY
BLADES_FRAME_SKIP = 6 // VELOCITY
BOAT_FRAME_SKIP = 160 // VELOCITY # only used for boat sound effect

WASP_COUNTDOWN = 12 // VELOCITY
BLADES_COUNTDOWN = 24 // VELOCITY

class Beetle(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (12 * SCALAR, 12 * SCALAR)
    
    def __init__(self):
        if Beetle.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "beetle-frames.png")
            Beetle.framesImage = view.loadScaledImage(imagePath)        
        animationFrames = view.processMovementFrames(Beetle.framesImage, 2)
        spriteFrames = DirectionalFrames(animationFrames, BEETLE_FRAME_SKIP)
        OtherSprite.__init__(self, spriteFrames)
        self.upright = False

    def processCollision(self, player):
        player.loseLife()
        return True
    
    # initialises a 'robot' movement strategy - moving along the given list of tiles
    def initMovement(self, level, tilePoints):
        OtherSprite.initMovement(self, level, tilePoints)
        self.pathPoints = []
        for tilePoint in tilePoints:
            self.pathPoints.append((tilePoint[0] * TILE_SIZE + self.position[0],
                                    tilePoint[1] * TILE_SIZE + self.position[1]))
        self.numPoints = len(tilePoints)
        self.currentPathPoint = self.pathPoints[0]
        self.pathPointIndex = 0
            
    def getMovement(self, player, trigger):
        currentPosition = self.mapRect.topleft
        x = self.currentPathPoint[0] - currentPosition[0]
        y = self.currentPathPoint[1] - currentPosition[1]
        if x == 0 and y == 0:
            self.pathPointIndex = (self.pathPointIndex + 1) % self.numPoints
            self.currentPathPoint = self.pathPoints[self.pathPointIndex]
            x = self.currentPathPoint[0] - currentPosition[0]
            y = self.currentPathPoint[1] - currentPosition[1]
        if x < 0:
            return MOVEMENT[LEFT]
        if x > 0:
            return MOVEMENT[RIGHT]
        if y < 0:
            return MOVEMENT[UP]
        if y > 0:
            return MOVEMENT[DOWN]
        # otherwise there is nowhere to move to
        return NO_MOVEMENT
    
    def playSound(self, frameIndex):
        if frameIndex == 1:
            self.eventBus.dispatchBeetleCrawlingEvent(BeetleCrawlingEvent())
        
class Wasp(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (9 * SCALAR, 12 * SCALAR)    

    def __init__(self):
        if Wasp.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "wasp-frames.png")
            Wasp.framesImage = view.loadScaledImage(imagePath)        
        animationFrames = view.processMovementFrames(Wasp.framesImage, 2)
        spriteFrames = DirectionalFrames(animationFrames, WASP_FRAME_SKIP)
        OtherSprite.__init__(self, spriteFrames)
        
    def processCollision(self, player):
        player.loseLife()
        return True
    
    def processMapExit(self):
        if self.mapRect.colliderect(self.rpgMap.mapRect):
            return False
        self.remove()
        return True
    
    # initialises a 'zoom' movement strategy - zooming towards the player vertically/horizontally
    def initMovement(self, level, tilePoints):
        OtherSprite.initMovement(self, level, tilePoints)
        self.upRect = Rect(self.baseRect.left, self.baseRect.top - VIEW_HEIGHT, self.baseRect.width, VIEW_HEIGHT)
        self.downRect = Rect(self.baseRect.left, self.baseRect.bottom, self.baseRect.width, VIEW_HEIGHT)
        self.leftRect = Rect(self.baseRect.left - VIEW_WIDTH, self.baseRect.top, VIEW_WIDTH, self.baseRect.height)
        self.rightRect = Rect(self.baseRect.right, self.baseRect.top, VIEW_WIDTH, self.baseRect.height)
        self.countdown = WASP_COUNTDOWN;
        self.zooming = False
        self.direction = None # this is also used to detect if the sprite has 'seen' the player
    
    def getMovement(self, player, trigger):
        if self.zooming:
            # print "zooming"
            return ZOOM_MOVEMENT[self.direction]
        if self.inView and self.level == player.level and not self.direction:
            metadata = NO_METADATA
            if self.leftRect.colliderect(player.baseRect):
                self.direction, metadata = LEFT, LEFT_METADATA
            elif self.rightRect.colliderect(player.baseRect):
                self.direction, metadata = RIGHT, RIGHT_METADATA
            elif self.upRect.colliderect(player.baseRect):
                self.direction, metadata = UP, UP_METADATA
            elif self.downRect.colliderect(player.baseRect):
                self.direction, metadata = DOWN, DOWN_METADATA
            return 0, 0, metadata
        # if direction is set, the sprite has 'seen' the player - countdown begins
        if self.direction:
            self.countdown -= 1
            if self.countdown == 0:
                self.zooming = True
                self.eventBus.dispatchWaspZoomingEvent(WaspZoomingEvent())
        return NO_MOVEMENT

class Blades(OtherSprite):
    
    framesImage = None
    
    baseRectSize = (TILE_SIZE, TILE_SIZE)    

    def __init__(self):
        if Blades.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "blades-frames.png")
            Blades.framesImage = view.loadScaledImage(imagePath)        
        animationFrames = view.processStaticFrames(Blades.framesImage, 10)
        spriteFrames = StaticFrames(animationFrames, BLADES_FRAME_SKIP)
        OtherSprite.__init__(self, spriteFrames, (0, -14))
        self.deactivate()

    def getBaseRectTop(self, baseRectHeight):
        return self.mapRect.bottom - baseRectHeight + 2 * SCALAR
                
    def processCollision(self, player):
        #frameIndex = self.spriteFrames.frameIndex
        if self.spriteFrames.frameIndex > 0:
            player.loseLife()
            return True
        return False
    
    # override
    def advanceFrame(self, increment, metadata):
        if increment:
            if self.active:
                self.image, frameIndex = self.spriteFrames.advanceFrame()
                if frameIndex == 0:
                    self.deactivate(self.level)
                if frameIndex == 2:
                    self.eventBus.dispatchBladesStabbingEvent(BladesStabbingEvent())
                return
            self.countdown -= 1
            if self.countdown == 0:
                self.activate()

    def deactivate(self, level = None):
        self.countdown = BLADES_COUNTDOWN;
        self.active = False
        if level:
            self.getMapTile().addNewLevel(level)

    def activate(self):
        self.active = True
        self.getMapTile().restore()
        
    def getMapTile(self):
        x, y = self.tilePosition[0], self.tilePosition[1]
        return self.rpgMap.mapTiles[x][y]
            
class Boat(OtherSprite):
    
    framesImage = None

    def __init__(self):
        if Boat.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "boat.png")
            Boat.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Boat.framesImage, 1)
        spriteFrames = StaticFrames(animationFrames, BOAT_FRAME_SKIP)
        OtherSprite.__init__(self, spriteFrames, (-10, 1))
        self.upright = False
        self.ticks = 0

    # override this so boats can never mask other sprites         
    def calculateZ(self):
        return 0
        
    def initMovement(self, level, tilePoints):
        OtherSprite.initMovement(self, level, tilePoints)
        self.tilePoints = tilePoints
        self.numPoints = len(tilePoints)
        self.currentPathPoint = self.toPathPoint(self.tilePoints[0])
        self.moving = False
            
    def getMovement(self, player, trigger):
        if self.numPoints < 2:
            return NO_MOVEMENT
        self.ticks = (self.ticks + 1) % 2
        if self.ticks:
            return NO_MOVEMENT
        if trigger and not self.moving:
            self.moving = True
            self.currentPathPoint = self.toPathPoint(self.tilePoints[1])
            self.playSound(0)
        currentPosition = self.mapRect.topleft
        x = self.currentPathPoint[0] - currentPosition[0]
        self.handleBoatStopped(x)
        if x < 0:
            return MOVEMENT[LEFT]
        if x > 0:
            return MOVEMENT[RIGHT]
        # otherwise there is nowhere to move to
        return NO_MOVEMENT
    
    def handleBoatStopped(self, x):
        if self.moving and abs(x) <= MOVE_UNIT:
            self.moving = False
            metadata = BoatMetadata(self.uid, self.tilePoints[1])
            self.eventBus.dispatchBoatStoppedEvent(BoatStoppedEvent(metadata))            
    
    def toPathPoint(self, tilePoint):
        return (tilePoint[0] * TILE_SIZE + self.position[0],
                tilePoint[1] * TILE_SIZE + self.position[1])
        
    def playSound(self, frameIndex):
        if self.moving and frameIndex == 0:
            self.eventBus.dispatchBoatMovingEvent(BoatMovingEvent())

    