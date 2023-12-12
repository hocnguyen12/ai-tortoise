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
        # weights :
        wi = [0 for i in range(7)]
        f = []
        f.append(lambda s, a:)  # distance de la mare la plus proche
        f.append(lambda s, a:)  # distance au chien
        f.append(lambda s, a:)  # distance de la laitue la plus proche
        f.append(lambda s, a:)  # taux d'exploration
        f.append(lambda s, a:)  # nbre de laitue restant
        f.append(lambda s, a: s.health_level)  # pt de vie
        f.append(lambda s, a: s.drink_level)  # pt de soif
        Q = lambda s, a: sum([self.wi[j] * self.f[j](s, a) for j in range(7)])

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
        self.alpha = float(0.5)
        self.epsilon = float(0.5)
        self.gamma = float(1)


    def distance_manhattan(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def update(self, state, action, nextState, reward, sensor):
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
            difference = reward + self.gamma * self.computeValueFromQValues(nextState, sensor) - self.Q(state,action)
            self.wi[i] += self.alpha * difference * self.f[i](state, action)

    def computeValueFromQValues(self, state, sensor): # U(s)
        """
        Returns max_action Q(state,action)
        where the max is over legal actions.
        V(s) = max_a Q(s,a)
        Note that if there are no legal actions, which is the case at the
        terminal state, you should return a value of 0.0.

        Useful attributes and methods:
        - self.alpha (learning rate)
        - self.discount (discount rate)
        - self.QValues[state, action] (the Qvalue Q(s,a))
        - self.getLegalActions(state): returns legal actions for a state
        """

        U = 0  # Note: if there are no legal actions, which is the case at the terminal state, you should return a value of 0.
        for a in self.getLegalActions(state, sensor):
            if self.Q(state, a) > U:
                U = self.Q(state, a)
        return U

    # actions : ['eat', 'drink', 'left', 'right', 'forward', 'wait']
    def getLegalActions(self, state, sensor):
        actions =  ['eat', 'drink', 'left', 'right', 'wait']
        if (sensor.free_ahead):
            actions.append('forward')
        return actions

    def computeActionFromQValues(self, state): # PI(s)
        """
        Comspute the best action to take in a state.
        a = argmax_a Q(s,a)

        Note that if there are no legal actions, which is the case at the terminal state,
        you should return None.

        Useful attributes and methods:
        - self.QValues[state, action] (the Qvalue Q(s,a))
        - self.getLegalActions(state): returns legal actions for a state
        """

        # *** YOUR CODE HERE ***

        actions = []
        action_max = self.getLegalActions(state)[0]
        U = 0
        for a in self.getLegalActions(state):
            if self.Q(state, a) == U:
                actions.append(a)
            if self.Q(state, a) > U:
                U = self.Q(state, a)
                action_max = a
        if len(actions) > 1:
            return random.choice(actions)
        return action_max

    def getAction(self, state):
        """
        Computes the action to take in the current state.  With
        probability self.epsilon, we should take a random action and
        take the best policy action otherwise.

        Note that if there are no legal actions, which is the case at
        the terminal state, you should choose None as the action.

        Instance variables you have access to
          - self.epsilon (exploration probability)

        HINT: You might want to use utils.flipCoin(prob)
        HINT: To pick randomly from a list, use random.choice(list)
        """

        legalActions = self.getLegalActions(state)
        if len(legalActions) == 0:
            return None
        # *** YOUR CODE HERE ***

        if utils.flipCoin(self.epsilon):
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

        # *** YOUR CODE HERE ***"
        self.state.update_state_from_sensor(sensor)
        self.state.display()
        return self.getAction(self.state)


##################################################################################
# Qvalues

class Counter(dict):
    """
    A counter keeps track of counts for a set of keys.

    The counter class is an extension of the standard python
    dictionary type.  It is specialized to have number values
    (integers or floats), and includes a handful of additional
    functions to ease the task of counting data.  In particular,
    all keys are defaulted to have value 0.  Using a dictionary:

    a = {}
    print a['test']

    would give an error, while the Counter class analogue:

    >>> a = Counter()
    >>> print a['test']
    0

    returns the default 0 value. Note that to reference a key
    that you know is contained in the counter,
    you can still use the dictionary syntax:

    >>> a = Counter()
    >>> a['test'] = 2
    >>> print a['test']
    2

    This is very useful for counting things without initializing their counts,
    see for example:

    >>> a['blah'] += 1
    >>> print a['blah']
    1

    The counter also includes additional functionality useful in implementing
    the classifiers for this assignment.  Two counters can be added,
    subtracted or multiplied together.  See below for details.  They can
    also be normalized and their total count and arg max can be extracted.
    """
    def __getitem__(self, idx):
        self.setdefault(idx, 0)
        return dict.__getitem__(self, idx)

    def incrementAll(self, keys, count):
        """
        Increments all elements of keys by the same count.

        >>> a = Counter()
        >>> a.incrementAll(['one','two', 'three'], 1)
        >>> a['one']
        1
        >>> a['two']
        1
        """
        for key in keys:
            self[key] += count

    def argMax(self):
        """
        Returns the key with the highest value.
        """
        if len(self.keys()) == 0: return None
        all = self.items()
        values = [x[1] for x in all]
        maxIndex = values.index(max(values))
        return all[maxIndex][0]

    def sortedKeys(self):
        """
        Returns a list of keys sorted by their values.  Keys
        with the highest values will appear first.

        >>> a = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> a['third'] = 1
        >>> a.sortedKeys()
        ['second', 'third', 'first']
        """
        sortedItems = self.items()
        compare = lambda x, y:  sign(y[1] - x[1])
        sortedItems.sort(cmp=compare)
        return [x[0] for x in sortedItems]

    def totalCount(self):
        """
        Returns the sum of counts for all keys.
        """
        return sum(self.values())

    def normalize(self):
        """
        Edits the counter such that the total count of all
        keys sums to 1.  The ratio of counts for all keys
        will remain the same. Note that normalizing an empty
        Counter will result in an error.
        """
        total = float(self.totalCount())
        if total == 0: return
        for key in self.keys():
            self[key] = self[key] / total

    def divideAll(self, divisor):
        """
        Divides all counts by divisor
        """
        divisor = float(divisor)
        for key in self:
            self[key] /= divisor

    def copy(self):
        """
        Returns a copy of the counter
        """
        return Counter(dict.copy(self))

    def __mul__(self, y ):
        """
        Multiplying two counters gives the dot product of their vectors where
        each unique label is a vector element.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['second'] = 5
        >>> a['third'] = 1.5
        >>> a['fourth'] = 2.5
        >>> a * b
        14
        """
        sum = 0
        x = self
        if len(x) > len(y):
            x,y = y,x
        for key in x:
            if key not in y:
                continue
            sum += x[key] * y[key]
        return sum

    def __radd__(self, y):
        """
        Adding another counter to a counter increments the current counter
        by the values stored in the second counter.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> a += b
        >>> a['first']
        1
        """
        for key, value in y.items():
            self[key] += value

    def __add__( self, y ):
        """
        Adding two counters gives a counter with the union of all keys and
        counts of the second added to counts of the first.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> (a + b)['first']
        1
        """
        addend = Counter()
        for key in self:
            if key in y:
                addend[key] = self[key] + y[key]
            else:
                addend[key] = self[key]
        for key in y:
            if key in self:
                continue
            addend[key] = y[key]
        return addend

    def __sub__( self, y ):
        """
        Subtracting a counter from another gives a counter with the union of all keys and
        counts of the second subtracted from counts of the first.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> (a - b)['first']
        -5
        """
        addend = Counter()
        for key in self:
            if key in y:
                addend[key] = self[key] - y[key]
            else:
                addend[key] = self[key]
        for key in y:
            if key in self:
                continue
            addend[key] = -1 * y[key]
        return addend