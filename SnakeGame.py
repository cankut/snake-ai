import numpy as np
from Common import DIRECTION, TURN, BOARD_OBJECT, ALL_TURNS, ALL_DIRECTIONS, DIRECTION_UNIT_VECTORS, DIRECTION_MARKERS, Log
from GameStatistics import GameStatistics
from Network import Network

class SnakeGame:

    @staticmethod
    def play(board_size, predictor: Network, max_moves, print_sensory = False):
    
        game = SnakeGame(board_size, max_moves=max_moves)
        
        while True:
            inputs = game.get_sensory_inputs()
            if(print_sensory):
                Log(str(inputs))
            index = predictor.predict(inputs)
            turn = ALL_TURNS[index]
            if(game.move(turn)):
                break

        return game

    @staticmethod
    def __init_free_positions(D: dict, board_size):
        D.clear()
        m = board_size
        x, y = np.meshgrid(range(0, m), range(0, m))
        coordinates = np.concatenate((x.reshape(-1, 1), y.reshape(-1, 1)), axis=1)
        for point in coordinates:
            D[tuple(point)] = 0

    def __init__(self, board_size, max_moves):

        self.__max_moves = max_moves            # defines maximum number of moves consecutively without eating apple
        self.__no_apple_counter = 0             # number of consecutive moves without eating apple
        self.__history = []                     # list of game states for each move
        self.__statistics = GameStatistics()    # statistics object that holds count for left/right/forward moves and snake size
        self.__body = []                        # list of snakes body part positions [x,y]. first is tail, last is head
        self.__apple = None                     # position of apple [x,y]
        self.__free_positions = dict()          # dictionary of free positions. keys are positions (x,y)
        self.__board_size = board_size          # side length of board

        self.__proximities = [1/i for i in range(1,board_size+1)]       # list of proximities denoting how much close to an object (apple, wall or body)
        self.__init_free_positions(self.__free_positions, board_size)

        self.__head_direction = np.random.choice(ALL_DIRECTIONS)

        head = np.random.randint(0, board_size, 2)
        self.__put_head(head)

        apple = self.__get_random_free_position()
        self.__put_apple(apple)
        
        self.__save_state()

    def __turn_head(self, turn: TURN):
        self.__statistics.turn(turn)
        current_direction_value = self.__head_direction.value
        self.__head_direction = ALL_DIRECTIONS[(current_direction_value + turn.value) % 4]

    def __get_random_free_position(self):
        frees = list(self.__free_positions.keys())
        n_free = len(frees)
        if n_free == 0:
            return None
        index = int(np.random.randint(0, n_free))
        free = frees[index]
        # todo: faster way to access random item in dictionary
        return np.array(free)

    def __is_free(self, position):
        return tuple(position) in self.__free_positions

    def __set_free(self, position):
        """
            Adds given position to list of empty positions.
        """   
        self.__free_positions[tuple(position)] = 0

    def __set_occupied(self, position):
        """
            Removes given position from list of empty positions.
        """
        if position is None:
            return
        del self.__free_positions[tuple(position)]

    def __put_apple(self, position):
        self.__apple = position
        self.__set_occupied(position)

    def __put_head(self, position):
        self.__body.append(position)
        self.__set_occupied(position)
        Log("head at: "+str(position) + " Looking: " + DIRECTION_MARKERS[self.__head_direction], level=0)

    def __move_head(self, position, is_apple_eaten):

        self.__body.append(position)  # add new head to body parts

        if is_apple_eaten == False:
            self.__no_apple_counter += 1 # increase no apple count
            tail = self.__body.pop(0)  # remove old tail
            self.__set_free(tail)
            self.__set_occupied(position)

        else:
            self.__no_apple_counter = 0 # reset no apple counter
            self.__statistics.eat() # update statistics
            new_apple = self.__get_random_free_position()
            self.__put_apple(new_apple) # put new apple on board

        Log("head at: "+str(position) + " Looking: " + DIRECTION_MARKERS[self.__head_direction], level=0)
        
    def __is_outside(self, position):
        m = self.__board_size
        x, y = position
        return x < 0 or x >= m or y < 0 or y >= m

    def __is_perfect_game(self):
        return len(self.__body) == (self.__board_size**2)

    def __save_state(self):
        if self.__apple is None:
            snapshot = self.__body[:], None, self.__head_direction
        else:
            snapshot = self.__body[:], self.__apple[:], self.__head_direction
        
        self.__history.append(snapshot)

    def __scan_direction(self, position, direction: DIRECTION):
        """
            Scans obstacles in given direction starting from position.
            
            Returns [apple_proximity, obstacle_proximity]
        """
        
        i = 0

        unit_step = DIRECTION_UNIT_VECTORS[direction]
        next = position

        while True:
            next = next + unit_step

            proximity = self.__proximities[i]

            if(self.__is_outside(next)): # wall
                return [0, proximity] 

            elif(np.array_equal(next, self.__apple)): # apple
                return [proximity, 0]

            elif(self.__is_free(next) == False): # body
                return [0, proximity]

            i += 1

    
    ### PUBLIC METHODS


    def get_sensory_inputs(self):
        """
            Scans 3 directions relative to head and gets proximity measures in order:
                
                Forward Apple, Forward Obstacle, Left Apple, Left Obstacle, Right Apple, Right Obstacle

            Returns [f_apple, f_obstacle, l_apple, l_obstacle, r_apple, r_obstacle]
        """
        head = self.__body[-1]

        d_forward = self.__head_direction
        d_left = ALL_DIRECTIONS[(d_forward.value + TURN.LEFT.value) % 4]
        d_right = ALL_DIRECTIONS[(d_forward.value + TURN.RIGHT.value) % 4]

        s_forward = self.__scan_direction(head, d_forward)
        s_left= self.__scan_direction(head, d_left)
        s_right = self.__scan_direction(head, d_right)

        return s_forward + s_left + s_right

    def get_statistics(self):
        """
            Returns move counts for left,right,forward and snake size
        """
        return self.__statistics.get()

    def get_fitness(self):
        l,r,f,size = self.get_statistics()
        bias_coef = 1
        if(l == 0 or r == 0):
            bias_coef = 0.1
        #total_moves = l+r+f
        #delta = abs(l-r)
        score = (bias_coef * size) #- delta*(0.1)
        return score

    def get_board_size(self):
        return self.__board_size

    def get_history(self):
        return self.__history

    def move(self, turn: TURN):

        Log("Command: "+str(turn), level=0)

        is_finished = False

        # change snake heads direction
        self.__turn_head(turn)

        # calculate heads next position
        head = self.__body[-1]
        next = head + DIRECTION_UNIT_VECTORS[self.__head_direction]

        # check if new head position is inside borders
        if self.__is_outside(next):
            is_finished = True

        # check if new head overlaps with apple
        elif np.array_equal(next, self.__apple):
            self.__move_head(next, is_apple_eaten=True)
            if(self.__is_perfect_game()):
                is_finished = True

        # check if new head overlaps with body
        elif self.__is_free(next) == False:
            is_finished = True

        # head is moving to empty
        else:
            self.__move_head(next, is_apple_eaten=False)

        if(self.__no_apple_counter >= self.__max_moves):
            is_finished = True

        self.__save_state()
        return is_finished





