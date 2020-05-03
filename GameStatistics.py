from Common import TURN

class GameStatistics:

    def __init__(self):
        self.__left = 0
        self.__right = 0
        self.__forward = 0
        self.__size = 1

    def turn(self, turn: TURN):

        if turn == TURN.LEFT:
            self.__left += 1
        elif turn == TURN.RIGHT:
            self.__right += 1
        else:
            self.__forward += 1

    def eat(self):
        self.__size += 1

    def get(self):
        """
            Returns counts for left,right,forward moves and size
        """
        return self.__left, self.__right, self.__forward, self.__size
