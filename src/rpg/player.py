#!/usr/bin/env python

import mapevents

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

from sprites import *
from events import PlayerFootstepEvent, PlayerFallingEvent, LifeLostEvent, EndGameEvent
from spriteframes import DirectionalFrames, StaticFrames
from view import NONE, UP, DOWN, LEFT, RIGHT, VIEW_WIDTH, VIEW_HEIGHT

PLAYER_FOOTSTEP_EVENT = PlayerFootstepEvent()
PLAYER_FALLING_EVENT = PlayerFallingEvent()

DIAGONAL_TICK = 3

NO_BOUNDARY = 0

FALL_UNIT = 2 * MOVE_UNIT

ULMO_FRAME_SKIP = 6 // VELOCITY

"""
Valid movement combinations - movement is keyed on direction bits and is stored
as a tuple (px, py, direction, diagonal)
""" 
MOVEMENT = {UP: (0, -MOVE_UNIT, UP, False),
            DOWN: (0, MOVE_UNIT, DOWN, False),
            LEFT: (-MOVE_UNIT, 0, LEFT, False),
            RIGHT: (MOVE_UNIT, 0, RIGHT, False),
            UP + LEFT: (-MOVE_UNIT, -MOVE_UNIT, UP, True),
            UP + RIGHT: (MOVE_UNIT, -MOVE_UNIT, UP, True),
            DOWN + LEFT: (-MOVE_UNIT, MOVE_UNIT, DOWN, True),
            DOWN + RIGHT: (MOVE_UNIT, MOVE_UNIT, DOWN, True)}

def getMovement(directionBits):
    if directionBits in MOVEMENT:
        return MOVEMENT[directionBits]
    return None

"""
An animated player controlled sprite.  This provides movement + masking by
extending MaskSprite, but all animation functionality is encapsulated here.
"""        
class Player(RpgSprite):
    
    def __init__(self, movingFrames, fallingFrames, position = (0, 0)):
        RpgSprite.__init__(self, movingFrames, position)
        # frames for when the player is moving/falling
        self.fallingFrames = fallingFrames
        self.movingFrames = movingFrames
        # view rect is the scrolling window onto the map
        self.viewRect = Rect((0, 0), (VIEW_WIDTH, VIEW_HEIGHT))
        # movement
        self.movement = None
        self.deferredMovement = None
        # pre-load shadow
        self.shadow = Shadow()
        # fixed sprites
        self.coinCount = None
        self.keyCount = None
        self.lives = None
        self.checkpointIcon = None
        # counters
        self.ticks = 0
        self.falling = 0

    """
    Base rect for the player extends beyond the bottom of the sprite image.
    """
    def getBaseRectTop(self, baseRectHeight):
        return self.mapRect.bottom + BASE_RECT_EXTEND - baseRectHeight
    
    """
    The view rect is entirely determined by what the player is doing.  Sometimes
    we move the view, sometimes we move the player - it just depends where the
    player is on the map.
    """
    def updateViewRect(self):
        # centre self.rect in the view
        px, py = (self.viewRect.width - self.rect.width) // 2, (self.viewRect.height - self.rect.height) // 2
        self.rect.topleft = (px, py)
        self.viewRect.topleft = (self.mapRect.left - px, self.mapRect.top - py)
        rpgMapRect = self.rpgMap.mapRect
        if rpgMapRect.contains(self.viewRect):
            return
        # the requested view falls partially outside the map - we need to move
        # the sprite instead of the view
        px, py = 0, 0
        if self.viewRect.left < 0:
            px = self.viewRect.left
        elif self.viewRect.right > rpgMapRect.right:
            px = self.viewRect.right - rpgMapRect.right
        if self.viewRect.top < 0:
            py = self.viewRect.top
        elif self.viewRect.bottom > rpgMapRect.bottom:
            py = self.viewRect.bottom - rpgMapRect.bottom
        self.rect.move_ip(px, py)
        self.viewRect.move_ip(-px, -py)
        
    """
    Main entry point into the player class.  Handles key presses, movement and
    interactions with the given sprite groups
    """
    def handleInteractions(self, keyPresses, gameSprites, visibleSprites):
        # have we triggered any events?
        self.update(gameSprites)
        # have we collided with any sprites?
        self.processCollisions(visibleSprites.sprites())
        # go ahead and handle user input
        directionBits, action = self.processKeyPresses(keyPresses)
        self.handleMovement(directionBits)
        if action:
            self.processActions(visibleSprites.sprites())
    
    """
    Takes the given key presses and converts them into direction bits + a boolean
    to indicate if the action key was pressed. 
    """
    def processKeyPresses(self, keyPresses):
        directionBits = NONE
        if keyPresses[K_UP]:
            directionBits += UP
        if keyPresses[K_DOWN]:
            directionBits += DOWN
        if keyPresses[K_LEFT]:
            directionBits += LEFT
        if keyPresses[K_RIGHT]:
            directionBits += RIGHT
        if keyPresses[K_SPACE]:
            return directionBits, True
        return directionBits, False
    
    """
    Moves the player + updates the view rect.  The control flow is as follows:
    > Check for deferred movement and apply if necessary.
    > Otherwise, check the requested movement is valid.
    > If valid, apply the requested movement.
    > If not valid, attempt to slide/shuffle the player.
    > If still not valid, check for a change in direction.
    """
    def handleMovement(self, directionBits):
        if self.falling:
            return
        movement = getMovement(directionBits)
        if not movement:
            return
        # check for deferred movement
        if movement == self.movement:
            self.ticks = (self.ticks + 1) % DIAGONAL_TICK
            if self.deferredMovement:
                level, direction, px, py = self.deferredMovement
                self.wrapMovement(level, direction, px, py)
                return
        else:
            self.ticks = 0
        # otherwise apply normal movement
        self.movement = movement
        px, py, direction, diagonal = movement
        # is the requested movement valid?
        newBaseRect = self.baseRect.move(px, py)
        valid, level = self.rpgMap.isMoveValid(self.level, newBaseRect)
        if valid:
            # if movement diagonal we only move 2 out of 3 ticks
            if diagonal and self.ticks == 0:
                self.deferMovement(level, direction, px, py)
            else:
                self.wrapMovement(level, direction, px, py)
            return
        # movement invalid but we might be able to slide or shuffle
        if diagonal:
            valid = self.slide(movement)
        else:
            valid = self.shuffle(movement)
        # movement invalid - apply a stationary change of direction if required
        if not valid and self.spriteFrames.direction != direction:
            self.setDirection(direction);
    
    """
    Slides the player. If the player is attempting to move diagonally, but is
    blocked, the vertical or horizontal component of their movement may still
    be valid.
    """
    def slide(self, movement):
        px, py, direction, diagonal = movement
        # check if we can slide horizontally
        xBaseRect = self.baseRect.move(px, 0)
        valid, level = self.rpgMap.isMoveValid(self.level, xBaseRect)
        if valid:
            self.deferMovement(level, direction, px, 0)
            return valid
        # check if we can slide vertically
        yBaseRect = self.baseRect.move(0, py)
        valid, level = self.rpgMap.isMoveValid(self.level, yBaseRect)                
        if valid:
            self.deferMovement(level, direction, 0, py)
        return valid
        
    """
    Shuffles the player.  Eg. if the player is attempting to move up, but is
    blocked, we will 'shuffle' the player left/right if there is valid movement
    available to the left/right.  This helps to align the player with steps,
    doorways, etc.
    """
    def shuffle(self, movement):
        px, py, direction, diagonal = movement
        # check if we can shuffle horizontally
        if px == 0:
            valid, level, shuffle = self.rpgMap.isVerticalValid(self.level, self.baseRect)
            if valid:
                self.deferMovement(level, direction, px + shuffle * MOVE_UNIT, 0)
            return valid
        # check if we can shuffle vertically
        valid, level, shuffle = self.rpgMap.isHorizontalValid(self.level, self.baseRect)
        if valid:
            self.deferMovement(level, direction, 0, py + shuffle * MOVE_UNIT)
        return valid
    
    """
    Calls applyMovement and performs some additional operations.
    """      
    def wrapMovement(self, level, direction, px, py, increment = 1):
        self.deferredMovement = None
        self.applyMovement(level, direction, px, py, increment)
        self.updateViewRect()
    
    """
    Stores the deferred movement and calls applyMovement with px, py = 0 for a
    'running on the spot' effect.
    """
    def deferMovement(self, level, direction, px, py):
        # store the deferred movement
        self.deferredMovement = (level, direction, px, py)
        self.applyMovement(level, direction, 0, 0)
    
    """
    Applies valid movement.
    """
    def applyMovement(self, level, myDirection, px, py, increment = 1):
        # move the player to its new location
        self.level = level
        self.doMove(px, py)
        # animate the player
        self.clearMasks()
        self.image, frameIndex = self.spriteFrames.advanceFrame(increment, direction = myDirection)
        if frameIndex == 1 or frameIndex == 3:
            self.eventBus.dispatchPlayerFootstepEvent(PLAYER_FOOTSTEP_EVENT)
        self.applyMasks()
    
    """
    Sets the direction without moving anywhere.
    """
    def setDirection(self, direction):
        self.applyMovement(self.level, direction, 0, 0)
        
    """
    Checks the requested movement falls within the map boundary.  If not,
    dispatches a boundary event containing information on the breach. 
    """ 
    def processBoundaryEvents(self):
        if self.rpgMap.mapRect.contains(self.mapRect):
            # we're within the boundary
            return
        boundary, tileRange = self.getBoundary()
        event = self.rpgMap.getBoundaryEvent(boundary, tileRange)
        if event:
            self.dispatchMapTransitionEvent(event)
            return
        # unknown boundary
        print "boundary!"
    
    """
    Returns the breached boundary and the tile range for that boundary.
    """
    def getBoundary(self):
        boundary = NO_BOUNDARY
        rpgMapRect = self.rpgMap.mapRect
        if self.mapRect.left < 0:
            boundary = LEFT
        elif self.mapRect.right > rpgMapRect.right:
            boundary = RIGHT
        if self.mapRect.top < 0:
            boundary = UP
        elif self.mapRect.bottom > rpgMapRect.bottom:
            boundary = DOWN
        return boundary, self.getTileRange(boundary)
    
    """
    Gets the range of tiles involved in the boundary breach.
    """
    def getTileRange(self, boundary):
        tx1, ty1 = self.getTilePoint(self.baseRect.left, self.baseRect.top)
        tx2, ty2 = self.getTilePoint(self.baseRect.right - 1, self.baseRect.bottom - 1)
        #print "(%s, %s) -> (%s, %s)" % (tx1, ty1, tx2, ty2)
        if boundary == UP or boundary == DOWN:
            return range(tx1, tx2 + 1)
        return range(ty1, ty2 + 1)
    
    """
    Gets the tile at the given pixel position.
    """
    def getTilePoint(self, px, py):
        return px // TILE_SIZE, py // TILE_SIZE
    
    """
    Positions the player relative to the given view.
    """    
    def relativeView(self, viewRect):
        self.rect.topleft = (self.mapRect.left - viewRect.left,
                             self.mapRect.top - viewRect.top)

    """
    Apply updates and return any map events.
    """
    def update(self, gameSprites):
        self.checkpointIcon.update()
        if self.falling:
            self.continueFalling()
            return
        self.processBoundaryEvents()
        event = self.rpgMap.getActionEvent(self.level, self.baseRect)
        if event:
            if event.type == mapevents.TILE_EVENT:
                self.dispatchMapTransitionEvent(event)
            elif event.type == mapevents.FALLING_EVENT:
                self.startFalling(gameSprites, event.downLevel)
    
    """
    Checks for an end game transition before dispatching the event.
    """        
    def dispatchMapTransitionEvent(self, event):
        if (event.transition.type == mapevents.END_GAME_TRANSITION):
            self.eventBus.dispatchEndGameEvent(EndGameEvent())
        else:
            self.eventBus.dispatchMapTransitionEvent(event)
        
    """
    Continues falling + detects if falling is complete.
    """    
    def continueFalling(self):
        self.wrapMovement(self.level, None, 0, FALL_UNIT);
        if self.falling % TILE_SIZE == 0:
            self.level -= 1
        self.falling -= FALL_UNIT
        if self.falling == 0:
            # falling is complete - swap back to moving frames
            self.clearMasks()
            self.spriteFrames = self.movingFrames.setState(self.spriteFrames)
            self.image, frameIndex = self.spriteFrames.advanceFrame(0)
            self.applyMasks()
            # remove shadow on next update
            self.shadow.toRemove = True
    
    """
    Starts falling by switching frames and adding a shadow to game sprites.
    """
    def startFalling(self, gameSprites, downLevel):
        #print "down: %s" % downLevel
        self.falling = downLevel * TILE_SIZE
        # swap to falling frames
        self.clearMasks()
        self.spriteFrames = self.fallingFrames.setState(self.spriteFrames)
        self.shadow = Shadow()
        self.shadow.setupFromPlayer(self, downLevel)
        gameSprites.add(self.shadow)
        self.eventBus.dispatchPlayerFallingEvent(PLAYER_FALLING_EVENT)
    
    """
    Processes collisions with other sprites in the given sprite collection.
    """
    def processCollisions(self, sprites):
        # if there are less than two sprites then self is the only sprite
        if len(sprites) < 2:
            return
        for sprite in sprites:
            if sprite.isIntersecting(self):
                sprite.processCollision(self)

    """
    Processes interactions with other sprites in the given sprite collection.
    """
    def processActions(self, sprites):
        # if there are less than two sprites then self is the only sprite
        if len(sprites) < 2:
            return
        for sprite in sprites:
            if sprite.isIntersecting(self):
                sprite.processAction(self)
    
    def getCoinCount(self):
        return self.coinCount.count;

    def setCoinCount(self, count):
        self.coinCount.setCount(count);

    def incrementCoinCount(self):
        self.coinCount.incrementCount()
        
    def getKeyCount(self):
        return self.keyCount.count;

    def setKeyCount(self, count):
        self.keyCount.setCount(count);

    def incrementKeyCount(self):
        self.keyCount.incrementCount()
        
    def decrementKeyCount(self):
        self.keyCount.incrementCount(-1)
        
    def loseLife(self):
        self.lives.incrementCount(-1)
        self.eventBus.dispatchLifeLostEvent(LifeLostEvent(self.isGameOver()))
        
    def isGameOver(self):
        return self.lives.noneLeft()
    
    def checkpointReached(self):
        self.checkpointIcon.activate()

"""
Extends the player sprite by defining a set of frame images.
"""    
class Ulmo(Player):
    
    movingFramesImage = None
    fallingFramesImage = None
    
    def __init__(self):
        if Ulmo.movingFramesImage is None:          
            imagePath = os.path.join(SPRITES_FOLDER, "ulmo-frames.png")
            Ulmo.movingFramesImage = view.loadScaledImage(imagePath)
        if Ulmo.fallingFramesImage is None:          
            imagePath = os.path.join(SPRITES_FOLDER, "ulmo-falling.png")
            Ulmo.fallingFramesImage = view.loadScaledImage(imagePath)
        animationFrames = view.processMovementFrames(Ulmo.movingFramesImage)
        movingFrames = DirectionalFrames(animationFrames, ULMO_FRAME_SKIP)
        animationFrames = view.processStaticFrames(Ulmo.fallingFramesImage)
        fallingFrames = StaticFrames(animationFrames)
        Player.__init__(self, movingFrames, fallingFrames, (1, -12))

"""
Shadow is really a static sprite, but is used when the player drops off a ledge.
For this reason it lives with the player class.
"""        
class Shadow(OtherSprite):
    
    framesImage = None
    
    def __init__(self):
        if Shadow.framesImage is None:    
            imagePath = os.path.join(SPRITES_FOLDER, "shadow.png")
            Shadow.framesImage = view.loadScaledImage(imagePath, None)        
        animationFrames = view.processStaticFrames(Shadow.framesImage, 1)
        spriteFrames = StaticFrames(animationFrames)
        OtherSprite.__init__(self, spriteFrames, (4, 2))
        self.upright = False
        
    def setupFromPlayer(self, player, downLevel):
        self.setup("shadow", player.rpgMap, player.eventBus)
        px = player.mapRect.topleft[0]
        py = player.mapRect.topleft[1] + downLevel * TILE_SIZE + player.image.get_height() - self.image.get_height()
        self.setPixelPosition(px, py, player.level - downLevel)
        
