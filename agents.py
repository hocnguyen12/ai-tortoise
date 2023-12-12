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
        self.lettuce_positions = []
        self.water_positions = []
        # weights :
        self.wi = [0 for i in range(7)]
        # features
        self.f = []
        self.f.append(self.distance_water)
        self.f.append(self.distance_dog)
        self.f.append(self.distance_lettuce)
        self.f.append(self.exploration_rate)
        self.f.append(self.remaining_lettuce)
        self.f.append(self.health_level)
        self.f.append(self.drink_level)

        self.Q = lambda s, a: sum([self.wi[j] * self.f[j](s, a) for j in range(7)])

    def save_weights(self, filename):
        with open(filename, 'w') as file:
            for weight in self.state.wi:
                file.write(f"{weight}\n")

    def distance_manhattan(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    ##############################
    # Feature functions
    def distance_water(self, state, action):
        if len(self.water_positions) == 0:
            return 100
        distance = self.distance_manhattan(self.x, self.y, self.water_positions[0][0], self.water_positions[0][1])
        for pond in self.water_positions :
            distance = min(distance, self.distance_manhattan(self.x, self.y, pond[0], pond[1]))
        return distance

    def distance_dog(self, state, action):
        return self.distance_manhattan(self.x, self.y, self.dogx, self.dogy)

    def distance_lettuce(self, state, action):
        if len(self.lettuce_positions) == 0:
            return 100
        distance = self.distance_manhattan(self.x, self.y, self.lettuce_positions[0][0], self.lettuce_positions[0][1])
        for lettuce in self.lettuce_positions:
           distance = min(distance, self.distance_manhattan(self.x, self.y, lettuce[0], lettuce[1]))
        return distance

    def exploration_rate(self, state, action):
        explored = 0
        for i in self.worldmap:
            if i != '?':
                explored += 1
        return explored/len(self.worldmap)

    def remaining_lettuce(self, state, action):
        return 0.16 * len(self.worldmap) - len(self.lettuce_positions)

    def health_level(self, state, action):
        return self.health_level

    def drink_level(self, state, action):
        return self.drink_level
    #################################

    def __deepcopy__( self, memo ):
        state = GameState()
        state.size = self.size
        state.worldmap = copy.deepcopy(self.worldmap, memo)
        state.size = self.size
        state.x = self.x
        state.y = self.y
        state.direction = self.direction
        state.drink_level = self.drink_level
        state.health_level = self.health_level
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
        self.free_ahead = sensor.free_ahead
        self.lettuce_here = sensor.lettuce_here
        self.lettuce_ahead = sensor.lettuce_ahead
        self.water_here =  sensor.water_here
        self.water_ahead = sensor.water_ahead


        # Update the map
        (directionx, directiony) = DIRECTIONTABLE[self.direction]
        if sensor.lettuce_here:
            self.worldmap[self.x][self.y] = LETTUCE
            #self.lettuce_positions.append((self.x, self.y))
        elif sensor.water_here:
            self.worldmap[self.x][self.y] = POUND
            #self.water_positions.append((self.x, self.y))
        else:
            self.worldmap[self.x][self.y] = GROUND
        if sensor.lettuce_ahead:
            self.worldmap[self.x + directionx][self.y + directiony] = LETTUCE
            self.lettuce_positions.append((self.x + directionx, self.y + directiony))
        elif sensor.water_ahead:
            self.worldmap[self.x + directionx][self.y + directiony] = POUND
            self.water_positions.append((self.x + directionx, self.y + directiony))
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
        self.alpha = float(0.5)
        self.epsilon = float(0.5)
        self.gamma = float(1)
        self.previous_state = None
        self.previous_action = None

    def update(self, action, nextState, reward):
        """
        The parent class calls this to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here.

        Useful attributes and methods:
        - self.alpha (learning rate)
        - self.discount (discount rate)
        - self.QValues[state, action] (the Qvalue Q(s,a))
        """

        # *** YOUR CODE HERE ***

        for i in range(7):
            difference = reward + self.gamma * self.computeValueFromQValues(nextState) - self.state.Q(self.state,action)
            self.state.wi[i] += self.alpha * difference * self.state.f[i](self.state, action)

    def computeValueFromQValues(self, state): # U(s)
        U = 0  # Note: if there are no legal actions, which is the case at the terminal state, you should return a value of 0.
        for a in self.getLegalActions():
            if self.state.Q(state, a) > U:
                U = self.state.Q(state, a)
        return U

    # actions : ['eat', 'drink', 'left', 'right', 'forward', 'wait']
    def getLegalActions(self):
        actions =  ['eat', 'drink', 'left', 'right', 'wait']
        if (self.state.free_ahead):
            actions.append('forward')
        return actions

    def computeActionFromQValues(self, state): # PI(s)
        actions = []
        action_max = self.getLegalActions()[0]
        U = 0
        for a in self.getLegalActions():
            if self.state.Q(state, a) == U:
                actions.append(a)
            if self.state.Q(state, a) > U:
                U = self.state.Q(state, a)
                action_max = a
        if len(actions) > 1:
            return random.choice(actions)
        return action_max

    def flipCoin(self, p):
        r = random.random()
        return r < p

    def getAction(self, state):
        legalActions = self.getLegalActions()
        if len(legalActions) == 0:
            return None

        if self.flipCoin(self.epsilon):
            action = random.choice(legalActions)
        else:
            action = self.computeActionFromQValues(state)
        return action

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


        if (self.previous_state is not None and self.previous_action is not None):
            self.update(self.previous_action, self.state, self.reward(self.previous_action))

        self.state.update_state_from_sensor(sensor)
        self.previous_state = self.state

        #self.state.display()
        action = self.getAction(self.state)
        self.previous_action = action
        return action

    def reward(self, action):
        if (action == 'eat' and self.state.lettuce_here):
            return 20
        if (self.state.water_here and action == 'drink' and self.state.drink_level < 20):
            return 10
        if (self.state.water_here and action == 'drink' and self.state.drink_level < 50):
            return 1
        if (self.state.water_here and action == 'drink' and self.state.drink_level < 75):
            return 0.5
        if ((not self.state.free_ahead) and action == 'forward'):
            return -10
        if (self.state.distance_manhattan(self.state.x, self.state.y, self.state.dogx, self.state.dogy) <= 5):
            return -5
        if (self.state.distance_manhattan(self.state.x, self.state.y, self.state.dogx, self.state.dogy) <= 5) and self.state.health_level < 20:
            return -10
        return 0