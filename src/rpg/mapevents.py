#! /usr/bin/env python

from view import DOWN

FALLING_EVENT = 0
TILE_EVENT = 1
BOUNDARY_EVENT = 2

BOUNDARY_TRANSITION = 1
SCENE_TRANSITION = 2
END_GAME_TRANSITION = 3
LIFE_LOST_TRANSITION = 4

"""
Map events are special events returned by the RpgMap API. They have two parts:

1. The event itself, eg. a BoundaryEvent indicates that the player has breached a
map boundary.

2. A transition that describes what happens next, eg. a SceneTransition indicates
that we need to replace the current map with another map.

For example, a BoundaryEvent might contain a BoundaryTransition (when the player
walks off the edge of one map and onto another) a SceneTransition (when the
player walks out of a cave) or an EndGameTransition.

Note that FallingEvent is a special case and does not contain a transition. 
"""
class MapEvent:
    def __init__(self, type, transition = None):
        self.type = type
        self.transition = transition

"""
Defines an event that occurs when the player walks off a ledge.
"""            
class FallingEvent(MapEvent):
    def __init__(self, downLevel):
        MapEvent.__init__(self, FALLING_EVENT)
        self.downLevel = downLevel

"""
Defines an event that occurs when the player steps on a tile that has an event.
"""
class TileEvent(MapEvent):
    def __init__(self, transition, x, y, level):
        MapEvent.__init__(self, TILE_EVENT, transition)
        self.x, self.y = x, y
        self.level = level

"""
Defines an event that occurs when the player walks off the edge of the map.
"""        
class BoundaryEvent(MapEvent):
    def __init__(self, transition, boundary, min, max = None):
        MapEvent.__init__(self, BOUNDARY_EVENT, transition)
        self.boundary = boundary
        if max:
            self.range = range(min, max + 1)
        else:
            self.range = [min]

"""
Transition base class.
"""
class Transition:
    def __init__(self, type, mapName = None):
        self.type = type
        self.mapName = mapName

"""
Defines a transition for when the player walks off the edge of one map and onto
another.
"""        
class BoundaryTransition(Transition):
    def __init__(self, mapName, boundary, modifier = 0):
        Transition.__init__(self, BOUNDARY_TRANSITION, mapName)
        self.boundary = boundary
        self.modifier = modifier

"""
Defines a transition for when we switch from one scene to another, eg. when the
player walks into a cave.
"""            
class SceneTransition(Transition):
    def __init__(self, mapName, x, y, level, direction = DOWN, boundary = None):
        Transition.__init__(self, SCENE_TRANSITION, mapName)
        self.tilePosition = (x, y)
        self.level = level
        self.direction = direction
        self.boundary = boundary

"""
Defines a transition for when the player reaches the end of the game. 
"""        
class EndGameTransition(Transition):
    def __init__(self):
        Transition.__init__(self, END_GAME_TRANSITION)
        
"""
Defines a transition for when the player loses a life and the scene is reset.
Note that this is very similar to a scene transition.
"""        
class LifeLostTransition(SceneTransition):
    def __init__(self, mapName, x, y, level):
        SceneTransition.__init__(self, mapName, x, y, level)
        self.type = LIFE_LOST_TRANSITION
