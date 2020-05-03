import numpy as np
import os , json
import glob
from typing import List
from Snake import Snake
from Genetics import Genetics
from Network import Network
from SnakeGame import SnakeGame
from Common import Log, generate_id, generate_chromosome

class Pool:

    def __init__(self, board_size, max_moves, predictor: Network):
        self.__board_size = board_size
        self.__max_moves = max_moves
        self.__chr_len = predictor.get_parameter_count()
        self.__predictor = predictor
        self.__snakes = []
        self.__epoch_winners = [] # list of winners for each epoch

    def seed(self, n):
        self.__snakes = [Snake(generate_id(),generate_chromosome(self.__chr_len), None, 0) for _ in range(n)]
        return self.__snakes

    def populate(self, pool_size, alpha):

        if self.__snakes == []:
            raise Exception('Cannot populate empty pool. Call pool.seed(n) to initialize pool.')

        n = len(self.__snakes)

        n_child = int(pool_size / n) - 1

        if n >= pool_size:
            raise Exception('Poolsize must be bigger than number of parents.')
        
        if pool_size % n > 0:
            raise Exception('Poolsize must be a multiple of number of parents.')

        new_pool = [] + self.__snakes

        for s in self.__snakes:
            children = Genetics.reproduce(s, n_child, alpha)
            new_pool += children
        
        self.__snakes = new_pool
        return self.__snakes

    def race(self, top, games_per_snake):
        
        n = len(self.__snakes)
        Log("Racing {} snakes...".format(n))

        scores = []

        for i,s in enumerate(self.__snakes):
            
            self.__predictor.load(s.get_chromosome())
            total_score = 0

            for _ in range(games_per_snake):

                game = SnakeGame.play(self.__board_size, self.__predictor, self.__max_moves)
                total_score += game.get_fitness()

            avg_fitness = total_score/games_per_snake
            Log("Snake [{}] Fitness = {}".format(i, avg_fitness), end="\r")
            scores.append(avg_fitness)
        
        Log("                                                               ",end="\r")

        best_indices = (np.array(scores)*-1).argsort()[:top]
        top_snakes = [self.__snakes[i] for i in best_indices]
        top_scores = [scores[i] for i in best_indices]

        self.__snakes = top_snakes
        
        winners = [snake.get_epoch_entry(score) for snake,score in zip(top_snakes,top_scores)]
        self.__epoch_winners.append(winners)

        return top_snakes , top_scores

    def get_size(self):
        return len(self.__snakes)

    def get_snakes(self):
        return self.__snakes
        
    def load(self, poolname):
        os.makedirs("pools/{}".format(poolname), exist_ok=True)
        files = glob.glob("pools/{}/[0-9]*.json".format(poolname))
        self.__snakes = [Snake.from_file(f) for f in files]
        
        epochs_path = "pools/{}/epochs.json".format(poolname)
        if(os.path.exists(epochs_path)):
            with open(epochs_path) as json_file:
                self.__epoch_winners = json.load(json_file)

    def save(self, poolname):

        with open("pools/{}/epochs.json".format(poolname), 'w') as outfile:
            json.dump(self.__epoch_winners, outfile)

        for i,s in enumerate(self.__snakes):
            file = "pools/{}/{}.json".format(poolname, i)
            s.save(file)

