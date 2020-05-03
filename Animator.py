import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.animation import FuncAnimation
from SnakeGame import SnakeGame
from Common import DIRECTION_UNIT_VECTORS, DIRECTION_MARKERS, BOARD_OBJECT, Log

class Animator:

    def __init__(self):
        self.__anim = None
    
    def __configure_grid(self, ax, board_size):
    
        m = board_size

        #move x axis ticks to top
        ax.xaxis.tick_top()

        #hide ticks
        ax.tick_params(length=0, which='both')

        #configure axes
        ax.set_xticks(np.arange(-.5, m, 1), minor=True)
        ax.set_yticks(np.arange(-.5, m, 1), minor=True)

        ax.set_xticks(np.arange(0, m, 1))
        ax.set_yticks(np.arange(0, m, 1))

        ax.set_xticklabels(np.arange(0, m, 1))
        ax.set_yticklabels(np.arange(0, m, 1))

        #draw gridlines
        ax.grid(which='minor', axis='both', linestyle='-', color='k', linewidth=2)

    def __dummy(self):
        pass

    def __to_matrix(self, body, apple, board_size):

        matrix = np.full((board_size,board_size), BOARD_OBJECT.EMPTY.value, dtype='int')
        
        if apple is not None:
            x,y = apple
            matrix[x,y] = BOARD_OBJECT.APPLE.value

        for b in body:
            x,y = b
            matrix[x,y] = BOARD_OBJECT.BODY.value

        if (len(body) > 1):
            x,y = body[0]
            matrix[x,y] = BOARD_OBJECT.TAIL.value

        return matrix

    def __draw(self, frame, board_size, history, im):
        
        Log("Frame {0}".format(frame), level=0)
        body, apple, head_direction = history[frame]
        matrix = self.__to_matrix(body, apple, board_size)

        ax = plt.gca()

        #clear markers
        for line in ax.lines:
            line.set_marker(None)

        #draw snake eyes
        head = body[-1]
        unit_direction = DIRECTION_UNIT_VECTORS[head_direction]
        direction_marker = DIRECTION_MARKERS[head_direction]

        eyes = head + (np.array(unit_direction) * .3) #draw eyes close to direction side
        plt.plot(eyes[0],eyes[1], marker=direction_marker, color='yellow')

        im.set_data(matrix.T)   

    def animate(self, game: SnakeGame, fps = 10):

        interval = 1000 / fps
        history = game.get_history()
        m = game.get_board_size()
        fig, ax = plt.subplots()
        cmap = colors.ListedColormap(['blue','white', 'green','red'])

        self.__configure_grid(ax, m)

        im = plt.imshow(np.zeros((m,m)), cmap=cmap, interpolation='none', vmin=-1, vmax=2)

        self.__anim = FuncAnimation(fig, self.__draw, init_func=self.__dummy, frames=len(history), fargs=[m, history, im], interval=interval, repeat=False)
        plt.show()