# ENSICAEN - École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE123

# @file agents.py
# @author Régis Clouard

import random
import copy
from math import sqrt
import utils

DIRECTIONTABLE = [(0, -1), (1, 0), (0, 1), (-1, 0)] # North, East, South, West

class TortoiseBrain:
    """
    The base class for various flavors of the tortoise brain.
    This an implementation of the Strategy design pattern.
    """
    def think( self, sensor ):
        raise Exception("Invalid Brain class, think() not implemented")

class RandomBrain( TortoiseBrain ):
    """
    An example of simple tortoise brain: acts randomly...
    """
    def init( self, grid_size ):
        pass

    def think( self, sensor ):
        return random.choice(['eat', 'drink', 'left', 'right', 'forward', 'forward', 'wait'])

class ReflexBrain( TortoiseBrain ):
    def init( self, grid_size ):
        pass

    def think( self, sensor ):
        # case 1: danger: dog
        if abs(sensor.dog_front) < 3 and abs(sensor.dog_right) < 3:
            if sensor.dog_front <= 0:
                if sensor.free_ahead:
                    return 'forward';
                elif sensor.dog_right > 0:
                    return 'left'
                else:
                    return 'right'
            elif sensor.dog_front > 0:
                if sensor.dog_right > 0:
                    return 'left';
                else:
                    return 'right'
        # increase the performance measure
        if sensor.lettuce_here and sensor.drink_level > 10: return 'eat'
        if sensor.water_ahead and sensor.drink_level < 50: return 'forward'
        if sensor.water_here and sensor.drink_level < 100: return 'drink'
        # Nothing to do: move
        if sensor.free_ahead:
            return random.choice(['forward', 'right', 'forward', 'wait', 'forward', 'forward', 'forward'])
        else:
            return random.choice(['right', 'left'])
        return random.choice(['eat', 'drink', 'left', 'right', 'forward', 'forward', 'wait'])

 #  ______                               _              
 # |  ____|                             (_)             
 # | |__    __  __   ___   _ __    ___   _   ___    ___ 
 # |  __|   \ \/ /  / _ \ | '__|  / __| | | / __|  / _ \
 # | |____   >  <  |  __/ | |    | (__  | | \__ \ |  __/
 # |______| /_/\_\  \___| |_|     \___| |_| |___/  \___|

# Character representation of environement elements 
WALL = 'X'
GROUND = '.'
UNKNOWN = '?'
LETTUCE = 'l'
POUND = 'p'
STONE = 's'
FREE = 'f'

class GameState():
    """ 
    This class is provided as an aid, but it is not required.
    You can modify it or even replace it with your own class.
    """

    def __init__(self, grid_size =0): 
        if grid_size > 0:
            self.size = grid_size
            self.worldmap = [ [  ((y in [0, self.size - 1] or  x in [0, self.size - 1]) and WALL) or UNKNOWN
                                 for x in range(self.size) ] for y in range(self.size) ]
    def __deepcopy__( self, memo ):
        state = GameState()
        state.size = self.size
        state.worldmap = copy.deepcopy(self.worldmap, memo)
        state.size = self.size
        state.x = self.x
        state.y = self.y
        state.direction = self.direction
        state.drink_level = self.drink_level
        state.dogx = self.dogx
        state.dogy = self.dogy
        return state

    def __eq__( self, other ):
        """ Used by the lists. """
        return self.x == other.x and self.y == other.y and self.direction == other.direction

    def __hash__(self):
        """ Used by the sets. """
        return hash((self.x, self.y, self.direction))

    def update_state_from_sensor( self, sensor ):
        """
        Updates the current environment from sensor information.
        """
        # Update the agent features
        self.drink_level = sensor.drink_level
        (self.x, self.y) = sensor.tortoise_position
        self.direction = sensor.tortoise_direction
        self.health_level = sensor.health_level

        # Update the map
        (directionx, directiony) = DIRECTIONTABLE[self.direction]
        if sensor.lettuce_here:
            self.worldmap[self.x][self.y] = LETTUCE
        elif sensor.water_here:
            self.worldmap[self.x][self.y] = POUND
        else:
            self.worldmap[self.x][self.y] = GROUND
        if sensor.lettuce_ahead:
            self.worldmap[self.x + directionx][self.y + directiony] = LETTUCE
        elif sensor.water_ahead:
            self.worldmap[self.x + directionx][self.y + directiony] = POUND
        elif sensor.free_ahead:
            self.worldmap[self.x + directionx][self.y + directiony] = GROUND
        elif self.worldmap[self.x + directionx][self.y + directiony] == UNKNOWN:
            self.worldmap[self.x + directionx][self.y + directiony] = STONE

        # Update the dog position
        if directionx == 0:
            self.dogx = self.x - directiony * sensor.dog_right
            self.dogy = self.y + directiony * sensor.dog_front
        else:
            self.dogx = self.x + directionx * sensor.dog_front
            self.dogy = self.y + directionx * sensor.dog_right

    def get_current_cell( self ):
        return self.worldmap[self.x][self.y]

    def display( self ):
        """
        For debugging purpose.
        """
        print("Memory..")
        for y in range(self.size):
            for x in range(self.size):
                print(self.worldmap[x][y], end=" ")
            print()

class RationalBrain( TortoiseBrain ):

    def init( self, grid_size ):
        self.state = GameState(grid_size)
        # *** YOUR CODE HERE ***"

    def think( self, sensor ):
        """
        Returns the best action with regard to the current state of the game.
        Available actions are ['eat', 'drink', 'left', 'right', 'forward', 'wait'].

        sensors attributes:
        sensor.free_ahead: there is no stone or wall one step ahead (boolean).
        sensor.lettuce_ahead: there is a lettuce plant one step ahead (boolean).
        sensor.lettuce_here: there is a lettuce plant at the current position (boolean).
        sensor.water_ahead: there is water one step ahead (boolean).
        sensor.water_here :there is water at the current position (boolean).
        sensor.drink_level : the level of water in the tortoise’s body, ranging from 100 to 0.
        sensor.health_level: the level of health in the tortoise’s body, ranging from 100 to 0.
        sensor.dog_front: the relative position of the dog, ie. the number of cells in front (positive) or behind (negative) the tortoise that it is.
        sensor.dog_right: the relative position of the dog to the right, ie. the number of cells to the right (positive) or left (negative) of the tortoise that it is.
        sensor.tortoise_position: the tortoise coordinates (x,y).
        sensor.tortoise_direction: the tortoise direction between 0 (north), 1 (east), 2 (south), and 3 (west).
        """

        # *** YOUR CODE HERE ***"
        utils.raiseNotDefined()