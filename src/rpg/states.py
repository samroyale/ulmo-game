#! /usr/bin/env python

import os
import pygame
import parser
import sprites
import view
import spritebuilder
import font
import mapevents

from pygame.locals import K_SPACE, Rect

from sprites import VELOCITY, MOVE_UNIT
from view import UP, DOWN, LEFT, RIGHT, SCALAR, VIEW_WIDTH, VIEW_HEIGHT

from events import TitleShownEvent, GameStartedEvent
from eventbus import EventBus
from registry import RegistryHandler, Registry
from player import Ulmo
from sounds import SoundHandler
from music import MusicPlayer
from fixedsprites import FixedCoin, CoinCount, KeyCount, Lives, CheckpointIcon

FRAMES_PER_SEC = 60 // VELOCITY

THIRTY_TWO = 32 // VELOCITY
SIXTY_FOUR = 64 // VELOCITY

ORIGIN = (0, 0)
X_MULT = VIEW_WIDTH // SIXTY_FOUR
Y_X_RATIO = float(VIEW_HEIGHT) / VIEW_WIDTH
DIMENSIONS = (VIEW_WIDTH, VIEW_HEIGHT)

# number of frames required to bring the player into view from an off-screen position
BOUNDARY_TICKS = {UP: 24 // VELOCITY,
                  DOWN: 24 // VELOCITY,
                  LEFT: 14 // VELOCITY,
                  RIGHT: 14 // VELOCITY}
DOORWAY_TICKS = {UP: 16 // VELOCITY,
                 DOWN: 16 // VELOCITY,
                 LEFT: 16 // VELOCITY,
                 RIGHT: 16 // VELOCITY}

PLAYER_OFF_SCREEN_START = (-2, 27)
PLAYER_ON_SCREEN_START = (7, 27)

pygame.display.set_caption("Ulmo's Adventure")
screen = pygame.display.set_mode(DIMENSIONS)

blackRect = view.createRectangle(DIMENSIONS)

gameFont = font.GameFont()
titleFont = font.TitleFont()

# globals
eventBus = None
soundHandler = None
registryHandler = None
musicPlayer = None
fixedSprites = None
player = None

def setup():
    global eventBus
    eventBus = EventBus()

    global soundHandler
    soundHandler = SoundHandler()
    eventBus.addCoinCollectedListener(soundHandler)
    eventBus.addKeyCollectedListener(soundHandler)
    eventBus.addDoorOpeningListener(soundHandler)
    eventBus.addPlayerFootstepListener(soundHandler)
    eventBus.addMapTransitionListener(soundHandler)
    eventBus.addEndGameListener(soundHandler)
    eventBus.addLifeLostListener(soundHandler)
    eventBus.addWaspZoomingListener(soundHandler)
    eventBus.addBeetleCrawlingListener(soundHandler)
    eventBus.addCheckpointReachedListener(soundHandler)
    eventBus.addPlayerFallingListener(soundHandler)
    eventBus.addBladesStabbingListener(soundHandler)
    eventBus.addBoatMovingListener(soundHandler)
    eventBus.addTitleShownListener(soundHandler)
    eventBus.addGameStartedListener(soundHandler)

    global registryHandler
    registryHandler = RegistryHandler()
    eventBus.addCoinCollectedListener(registryHandler)
    eventBus.addKeyCollectedListener(registryHandler)
    eventBus.addDoorOpenedListener(registryHandler)
    eventBus.addBoatStoppedListener(registryHandler)
    eventBus.addCheckpointReachedListener(registryHandler)

    global musicPlayer
    musicPlayer = MusicPlayer()

def showTitle(newGame = False):
    if newGame:
        setup()
    # return the title state
    return TitleState()

def startGame(cont = False, registry = None):
    registry = getRegistry(cont, registry)
    
    # create fixed sprites
    global fixedSprites
    fixedSprites = pygame.sprite.Group()
    fixedCoin = FixedCoin((27, 3))
    coinCount = CoinCount(registry.coinCount, (38, 3))
    keyCount = KeyCount(registry.keyCount, (0, 3))
    lives = Lives(2, (3, 3))
    checkpointIcon = CheckpointIcon((-11, -11))
    fixedSprites.add(fixedCoin, lives, coinCount, keyCount, checkpointIcon)
    
    # create player
    global player
    player = Ulmo()
    player.coinCount = coinCount
    player.keyCount = keyCount
    player.lives = lives
    player.checkpointIcon = checkpointIcon
    # create the map
    rpgMap = parser.loadRpgMap(registry.mapName)
    player.setup("ulmo", rpgMap, eventBus)
    # set the start position
    player.setTilePosition(registry.playerPosition[0],
                           registry.playerPosition[1],
                           registry.playerLevel)

    # return the play state
    return PlayState()

def getRegistry(cont, registry):
    if cont:
        registryHandler.switchToSnapshot()
        return registryHandler.registry
    if not registry:
        #registry = Registry("unit", (4, 6), 1)
        #registry = Registry("drops", (12, 7), 5)
        #registry = Registry("forest", (11, 8), 3)
        #registry = Registry("start", (22, 24), 4)
        registry = Registry("start", PLAYER_ON_SCREEN_START, 1)
        #registry = Registry("central", (6, 22), 2) # 0.93
    registryHandler.setRegistry(registry)
    return registry
    
def hidePlayer(boundary, mapRect, modifier = None):
    playerRect = player.mapRect
    px, py = playerRect.topleft
    if modifier:
        px, py = [i + modifier * view.TILE_SIZE for i in playerRect.topleft]
    # we position the player just off the screen and then use the ShowPlayer
    # state to bring the player into view                 
    if boundary == UP:
        py = mapRect.bottom
    elif boundary == DOWN:
        py = 0 - playerRect.height
    elif boundary == LEFT:
        px = mapRect.right
    else: # boundary == RIGHT
        px = 0 - playerRect.width             
    player.setPixelPosition(px, py)

def sceneZoomIn(screenImage, ticks):
    xBorder = (ticks + 1) * X_MULT
    yBorder = xBorder * Y_X_RATIO
    screen.blit(blackRect, ORIGIN)
    extract = Rect(xBorder, yBorder, VIEW_WIDTH - xBorder * 2, VIEW_HEIGHT - yBorder * 2)
    screen.blit(screenImage, (xBorder, yBorder), extract)
    pygame.display.flip()

def sceneZoomOut(screenImage, ticks):
    xBorder = (THIRTY_TWO - (ticks + 1)) * X_MULT
    yBorder = xBorder * Y_X_RATIO
    extract = Rect(xBorder, yBorder, VIEW_WIDTH - xBorder * 2, VIEW_HEIGHT - yBorder * 2)
    screen.blit(screenImage, (xBorder, yBorder), extract)
    pygame.display.flip()

"""
The title state brings the title screen into view, loading the first map and
initiates the start state.  It's possible to skip the start state by commenting
in a couple of lines below.
"""    
class TitleState:
    
    def __init__(self):
        imagePath = os.path.join("images", "horizon.png")
        self.backgroundImage = view.loadScaledImage(imagePath)
        imagePath = os.path.join("images", "title.png")
        self.titleImage = view.loadScaledImage(imagePath, view.TRANSPARENT_COLOUR)
        self.playLine = titleFont.getTextImage("PRESS SPACE TO PLAY")
        self.titleTicks = self.getTitleTicks()
        self.startRegistry = Registry("start", PLAYER_OFF_SCREEN_START, 1)
        self.screenImage = None
        self.playState = None
        self.started = False
        self.ticks = 0
        
    def getTitleTicks(self):
        return (self.backgroundImage.get_height() - VIEW_HEIGHT) * 2 // SCALAR // VELOCITY
             
    def execute(self, keyPresses):
        if self.started:
            nextState = self.gameStarted()
            if nextState:
                return nextState
        elif self.ticks < self.titleTicks:
            if self.ticks == 40:
                musicPlayer.playTrack("title")
            x, y = 0, self.ticks * MOVE_UNIT // 2
            screen.blit(self.backgroundImage, ORIGIN, Rect(x, y, VIEW_WIDTH, VIEW_HEIGHT))        
            pygame.display.flip()
        elif self.ticks == self.titleTicks + THIRTY_TWO:
            x, y = (VIEW_WIDTH - self.titleImage.get_width()) // 2, 26 * SCALAR
            screen.blit(self.titleImage, (x, y))
            pygame.display.flip()
            eventBus.dispatchTitleShownEvent(TitleShownEvent());
        elif self.ticks == self.titleTicks + SIXTY_FOUR:
            self.screenImage = screen.copy()
            self.playState = startGame(False, self.startRegistry)
            #self.playState = startGame() # SKIP START
            self.showPlayLine(self.playLine)
            eventBus.dispatchTitleShownEvent(TitleShownEvent());            
        elif self.ticks > self.titleTicks + SIXTY_FOUR:
            if keyPresses[K_SPACE]:
                self.ticks, self.started = 0, True
                eventBus.dispatchGameStartedEvent(GameStartedEvent());            
                return
        self.ticks += 1
    
    def gameStarted(self):
        if self.ticks % 3 == 0:
            if self.ticks // 3 % 2:
                self.showPlayLine(self.playLine)
            else:
                self.showPlayLine()
        if self.ticks > 18:
            return StartState(self.playState)
            #return self.playState.start() # SKIP START
            
    def showPlayLine(self, playLine = None):
        if playLine:
            x, y = (VIEW_WIDTH - playLine.get_width()) // 2, 88 * SCALAR
            screen.blit(playLine, (x, y))
        else:
            screen.blit(self.screenImage, ORIGIN)
        pygame.display.flip()
        

"""
The start state vertically scrolls the first map into view and initiates the
show boat state.  It's possible to skip the show boat state by commenting in a
line below.
"""
class StartState:
    
    def __init__(self, playState):
        self.screenImage = screen.copy()
        self.nextImage = view.createRectangle(DIMENSIONS)
        self.playState = playState
        self.viewRect = player.viewRect.copy()
        self.viewRect.top = 0
        self.ticks = 0
        musicPlayer.longFadeoutCurrentTrack()
        
    def execute(self, keyPresses):
        if self.ticks < VIEW_HEIGHT // MOVE_UNIT:
            player.relativeView(self.viewRect)
            self.playState.drawMapView(self.nextImage, self.viewRect)
            self.screenWipeUp((self.ticks + 1) * MOVE_UNIT)
        else:
            self.viewRect.move_ip(0, MOVE_UNIT)
            player.relativeView(self.viewRect)
            self.playState.drawMapView(screen, self.viewRect)
            # stop when the view rect is in line with the player's view rect
            if self.viewRect.top == player.viewRect.top:
                return ShowBoatState(self.playState)
                #return self.playState.start() // SKIP SHOW BOAT
        pygame.display.flip()
        self.ticks += 1

    def screenWipeUp(self, sliceHeight):
        screen.blit(self.screenImage, ORIGIN, Rect(0, sliceHeight, VIEW_WIDTH, VIEW_HEIGHT - sliceHeight))
        screen.blit(self.nextImage, (0, VIEW_HEIGHT - sliceHeight), Rect(0, 0, VIEW_WIDTH, sliceHeight))

"""
The show boat state brings the boat + player to the on screen start position.
It returns the play state once the boat has stopped.
"""
class ShowBoatState:
    
    def __init__(self, nextPlayState):
        self.playState = nextPlayState
        self.boatStoppedEvent = None
        self.ticks = 0
        # listen for boat stopped events
        eventBus.addBoatStoppedListener(self)
        
    def execute(self, keyPresses):
        if self.boatStoppedEvent:
            playerPosition = self.boatStoppedEvent.getMetadata().endPosition
            registryHandler.setPlayerPosition(playerPosition)
            registryHandler.takeSnapshot()
            return self.playState.start()
        self.showPlayer(MOVE_UNIT, 0)
        self.ticks += 1
        
    def showPlayer(self, px, py):
        if self.ticks % 2:
            player.wrapMovement(player.level,
                                player.spriteFrames.direction,
                                px, py, 0)
        self.playState.drawMapView(screen, player.viewRect, trigger = 1)
        pygame.display.flip()
        
    def boatStopped(self, boatStoppedEvent):
        self.boatStoppedEvent = boatStoppedEvent

"""
Main play state for the game - handles player movement, sprite updates and drawing
the map view.  It also listens for a number of events which result in new states
being returned.
"""                                            
class PlayState:
    
    def __init__(self):
        # must set the player map + position before we create this state
        player.updateViewRect()
        # add the player to the visible group
        self.visibleSprites = sprites.RpgSprites(player)
        # create more sprites
        self.gameSprites = spritebuilder.createSpritesForMap(player.rpgMap, eventBus, registryHandler.registry)
        
    # listen for map transition, life lost and end game events
    def start(self):
        self.eventCaptured = False
        self.mapTransitionEvent = None
        self.lifeLostEvent = None
        self.endGameEvent = None
        eventBus.addMapTransitionListener(self)
        eventBus.addLifeLostListener(self)
        eventBus.addEndGameListener(self)
        musicPlayer.playTrack(player.rpgMap.music)
        return self
                             
    def execute(self, keyPresses):
        nextState = self.handleEvents()
        if nextState:
            return nextState
        player.handleInteractions(keyPresses, self.gameSprites, self.visibleSprites)
        # draw the player map view to the screen
        self.drawPlayerMapView(screen)
        pygame.display.flip()
        
    def handleEvents(self):
        if not self.eventCaptured:
            return None
        if self.mapTransitionEvent:
            transition = self.mapTransitionEvent.transition 
            if transition:
                if transition.type == mapevents.BOUNDARY_TRANSITION:
                    return BoundaryTransitionState(transition)
                if transition.type == mapevents.SCENE_TRANSITION:
                    return SceneTransitionState(transition)
        if self.lifeLostEvent:
            if self.lifeLostEvent.gameOver:
                return GameOverState()
            return SceneTransitionState(self.lifeLostTransition())
        if self.endGameEvent:
            return EndGameState()    
    
    def drawPlayerMapView(self, surface):
        self.drawMapView(surface, player.viewRect)
        fixedSprites.draw(surface)
           
    def drawMapView(self, surface, viewRect, increment = 1, trigger = 0):
        surface.blit(player.rpgMap.mapImage, ORIGIN, viewRect)
        # if the sprite being updated is in view it will be added to visibleSprites as a side-effect
        self.gameSprites.update(player, self.visibleSprites, viewRect, increment, trigger)
        self.visibleSprites.draw(surface)
    
    def lifeLostTransition(self):
        registryHandler.switchToSnapshot()
        registry = registryHandler.registry
        player.setCoinCount(registry.coinCount)
        player.setKeyCount(registry.keyCount)
        return mapevents.LifeLostTransition(registry.mapName,
                                            registry.playerPosition[0],
                                            registry.playerPosition[1],
                                            registry.playerLevel)
        
    def mapTransition(self, mapTransitionEvent):
        self.mapTransitionEvent, self.eventCaptured = mapTransitionEvent, True
        
    def lifeLost(self, lifeLostEvent):
        self.lifeLostEvent, self.eventCaptured = lifeLostEvent, True
        
    def endGame(self, endGameEvent):
        self.endGameEvent, self.eventCaptured = endGameEvent, True

"""
The scene transition state switches from one scene to another and then brings the
player into view.  Typically this would occur when the player walks into/out of a
cave but it also handles life lost events.
"""        
class SceneTransitionState:
    
    def __init__(self, transition):
        self.transition = transition
        self.screenImage = screen.copy()
        self.playState = None
        self.ticks = 0
             
    def execute(self, keyPresses):
        if self.ticks < THIRTY_TWO:
            sceneZoomIn(self.screenImage, self.ticks)
        elif self.ticks < SIXTY_FOUR:
            if self.ticks == THIRTY_TWO:
                self.initPlayState()
            sceneZoomOut(self.screenImage, self.ticks - THIRTY_TWO)
        else:
            if self.transition.type == mapevents.LIFE_LOST_TRANSITION:
                return self.playState.start()
            # else just a regular scene transition
            direction = player.spriteFrames.direction
            if self.transition.boundary:
                return ShowPlayerState(direction, self.playState, BOUNDARY_TICKS[direction])
            return ShowPlayerState(direction, self.playState, DOORWAY_TICKS[direction])
        self.ticks += 1
        
    def initPlayState(self):
        # load the next map
        nextRpgMap = parser.loadRpgMap(self.transition.mapName)
        player.rpgMap = nextRpgMap
        # set player position
        player.setTilePosition(self.transition.tilePosition[0],
                               self.transition.tilePosition[1],
                               self.transition.level)
        # hide player if required
        if self.transition.boundary:
            hidePlayer(self.transition.boundary, nextRpgMap.mapRect)
        # create play state
        self.playState = PlayState()
        # setting the direction will also apply masks
        player.setDirection(self.transition.direction)
        # extract the next image from the play state
        self.playState.drawMapView(self.screenImage, player.viewRect, 0)           

"""
The boundary transition state provides seamless fast scrolling onto the next map
and then brings the player into view.  This would occur when the player walks off 
the edge of the current map.    
"""            
class BoundaryTransitionState:
    
    def __init__(self, transition):
        self.transition = transition
        self.boundary = transition.boundary
        self.screenImage = screen.copy()
        self.nextImage = view.createRectangle(DIMENSIONS)
        self.playState = None
        self.ticks = 0
                     
    def execute(self, keyPresses):
        if self.ticks < THIRTY_TWO:
            if self.ticks == 0:
                self.initPlayState()
            sliceWidth = self.ticks * X_MULT * 2
            sliceHeight = sliceWidth * Y_X_RATIO
            if self.boundary == UP:
                self.screenWipeDown(sliceHeight)
            elif self.boundary == DOWN:
                self.screenWipeUp(sliceHeight)
            elif self.boundary == LEFT:
                self.screenWipeRight(sliceWidth)
            else: # self.boundary == RIGHT
                self.screenWipeLeft(sliceWidth)
            pygame.display.flip()
        else:
            return ShowPlayerState(self.boundary, self.playState, BOUNDARY_TICKS[self.boundary])
        self.ticks += 1
        
    def initPlayState(self):
        # load the next map
        nextRpgMap = parser.loadRpgMap(self.transition.mapName)
        player.rpgMap = nextRpgMap
        player.spriteFrames.direction = self.boundary
        # set the new position
        hidePlayer(self.boundary, nextRpgMap.mapRect, self.transition.modifier)
        # create play state
        self.playState = PlayState()
        # extract the next image from the play state
        self.playState.drawMapView(self.nextImage, player.viewRect, 0)

    def screenWipeUp(self, sliceHeight):
        screen.blit(self.screenImage, ORIGIN, Rect(0, sliceHeight, VIEW_WIDTH, VIEW_HEIGHT - sliceHeight))
        screen.blit(self.nextImage, (0, VIEW_HEIGHT - sliceHeight), Rect(0, 0, VIEW_WIDTH, sliceHeight))                
        
    def screenWipeDown(self, sliceHeight):
        screen.blit(self.screenImage, (0, sliceHeight), Rect(0, 0, VIEW_WIDTH, VIEW_HEIGHT - sliceHeight))
        screen.blit(self.nextImage, ORIGIN, Rect(0, VIEW_HEIGHT - sliceHeight, VIEW_WIDTH, sliceHeight))                
    
    def screenWipeLeft(self, sliceWidth):
        screen.blit(self.screenImage, ORIGIN, Rect(sliceWidth, 0, VIEW_WIDTH - sliceWidth, VIEW_HEIGHT))
        screen.blit(self.nextImage, (VIEW_WIDTH - sliceWidth, 0), Rect(0, 0, sliceWidth, VIEW_HEIGHT))                
    
    def screenWipeRight(self, sliceWidth):
        screen.blit(self.screenImage, (sliceWidth, 0), Rect(0, 0, VIEW_WIDTH - sliceWidth, VIEW_HEIGHT))
        screen.blit(self.nextImage, ORIGIN, Rect(VIEW_WIDTH - sliceWidth, 0, sliceWidth, VIEW_HEIGHT))                

"""
The show player state is used by scene and boundary transitions to bring the
player into view from an off screen position, within a doorway, etc.
"""        
class ShowPlayerState:
    
    def __init__(self, boundary, nextPlayState, tickTarget):
        self.boundary = boundary
        self.playState = nextPlayState
        self.tickTarget = tickTarget
        self.ticks = 0
        
    def execute(self, keyPresses):
        if self.ticks > self.tickTarget:
            return self.playState.start()
        px, py = 0, 0
        if self.boundary == UP:
            py = -MOVE_UNIT
        elif self.boundary == DOWN:
            py = MOVE_UNIT
        elif self.boundary == LEFT:
            px = -MOVE_UNIT
        else: # self.boundary == RIGHT
            px = MOVE_UNIT
        self.showPlayer(px, py)
        self.ticks += 1

    def showPlayer(self, px, py):
        player.wrapMovement(player.level,
                            player.spriteFrames.direction,
                            px, py)
        self.playState.drawMapView(screen, player.viewRect)
        pygame.display.flip()

"""
The game over state provides a 'continue' option before either starting the game
or going back to the title screen.  
"""
class GameOverState:
    
    def __init__(self):
        self.screenImage = screen.copy()
        self.topLine1 = gameFont.getTextImage("BRAVE ADVENTURER")
        self.topLine2 = gameFont.getTextImage("YOU ARE DEAD")
        self.topLine3 = gameFont.getTextImage("CONTINUE... 10")
        self.lowLine1 = gameFont.getTextImage("PRESS SPACE")
        self.lowLine2 = gameFont.getTextImage("TO PLAY AGAIN")
        self.blackRect = view.createRectangle(self.topLine3.get_size(), view.BLACK)
        #self.continueOffered = True if registryHandler.snapshot.checkpoint else False
        self.continueOffered = True
        self.countdown = None
        self.countdownTopleft = None
        self.ticks = 0
        musicPlayer.fadeoutCurrentTrack()
             
    def execute(self, keyPresses):
        if self.countdown:
            if (self.ticks - SIXTY_FOUR) % FRAMES_PER_SEC == 0:
                self.updateCountdown()
                if not self.countdown:
                    return showTitle()
        if self.ticks < THIRTY_TWO:
            sceneZoomIn(self.screenImage, self.ticks)
        elif self.ticks == THIRTY_TWO:
            x, y = (VIEW_WIDTH - self.topLine1.get_width()) // 2, 32 * SCALAR
            screen.blit(self.topLine1, (x, y))
            x, y = (VIEW_WIDTH - self.topLine2.get_width()) // 2, 44 * SCALAR
            screen.blit(self.topLine2, (x, y))
            if self.continueOffered:
                x, y = (VIEW_WIDTH - self.topLine3.get_width()) // 2, 56 * SCALAR
                screen.blit(self.topLine3, (x, y))
                # set the countdown topleft for later
                self.countdownTopleft = (x, y)
            pygame.display.flip()
        elif self.ticks == SIXTY_FOUR:
            x, y = (VIEW_WIDTH - self.lowLine1.get_width()) // 2, VIEW_HEIGHT - 42 * SCALAR
            screen.blit(self.lowLine1, (x, y))
            x, y = (VIEW_WIDTH - self.lowLine2.get_width()) // 2, VIEW_HEIGHT - 30 * SCALAR
            screen.blit(self.lowLine2, (x, y))
            pygame.display.flip()
            if self.continueOffered:
                self.countdown = 10
        elif self.ticks > SIXTY_FOUR:
            if keyPresses[K_SPACE]:
                return startGame(True).start()
        self.ticks += 1
        
    def updateCountdown(self):
        self.countdown = self.countdown - 1
        countdownLine = gameFont.getTextImage("CONTINUE... " + str(self.countdown))
        screen.blit(self.blackRect, self.countdownTopleft)
        if self.countdown > 0:
            screen.blit(countdownLine, self.countdownTopleft)
            pygame.display.flip()

"""
The end game state provides an ending (of sorts!) before going back to the title screen. 
"""
class EndGameState:
    
    def __init__(self):
        self.screenImage = screen.copy()
        self.topLine1 = gameFont.getTextImage("YOUR ADVENTURE IS")
        self.topLine2 = gameFont.getTextImage("AT AN END... FOR NOW!")
        self.topLine3 = gameFont.getTextImage("YOU FOUND " + str(player.getCoinCount()) + "/10 COINS");
        self.lowLine1 = gameFont.getTextImage("PRESS SPACE")
        self.ticks = 0
        musicPlayer.fadeoutCurrentTrack()
             
    def execute(self, keyPresses):
        if self.ticks < THIRTY_TWO:
            sceneZoomIn(self.screenImage, self.ticks)
        elif self.ticks == THIRTY_TWO:
            x, y = (VIEW_WIDTH - self.topLine1.get_width()) // 2, 32 * SCALAR
            screen.blit(self.topLine1, (x, y))
            x, y = (VIEW_WIDTH - self.topLine2.get_width()) // 2, 44 * SCALAR
            screen.blit(self.topLine2, (x, y))
            x, y = (VIEW_WIDTH - self.topLine3.get_width()) // 2, 56 * SCALAR
            screen.blit(self.topLine3, (x, y))
            pygame.display.flip()
        elif self.ticks == SIXTY_FOUR:
            x, y = (VIEW_WIDTH - self.lowLine1.get_width()) // 2, VIEW_HEIGHT - 30 * SCALAR
            screen.blit(self.lowLine1, (x, y))
            pygame.display.flip()
        elif self.ticks > SIXTY_FOUR:
            if keyPresses[K_SPACE]:
                return showTitle()
        self.ticks += 1
