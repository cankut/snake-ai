import numpy as np
import os
import glob
from Common import ALL_TURNS, Log
from SnakeGame import SnakeGame
from Network import Network
from Animator import Animator
from Snake import Snake
from typing import List
from Pool import Pool

def test_snake(snake, number_of_games, board_size, max_moves, predictor: Network):

    Log("Testing performance on {} games...".format(number_of_games))

    snake_id = snake.get_id()
    generation = snake.get_generation()
    Log("Snake Id = {}".format(snake_id))
    Log("Generation = {}".format(generation))

    network.load(snake.get_chromosome())

    scores = []
    stats = []
    games = []

    for _ in range(number_of_games):
        game = SnakeGame.play(board_size, network, max_moves)
        games.append(game)
        scores.append(game.get_fitness())
        stats.append(game.get_statistics())
        
    best_indices = (np.array(scores)*-1).argsort()
    
    for i in best_indices:
        l,r,f,size = stats[i]
        fitness = scores[i]
        Log("Fitness: {} - L/R - Size : {}/{} - {}".format(fitness, l,r,size))
    
    Log("Average Fitness: {}".format(np.mean(scores)))

    best_game = games[best_indices[0]]
    worst_game = games[best_indices[-1]]

    return  best_game, worst_game

BOARD_SIZE = 10
MAX_MOVES = 100
ALPHA = 0.5     # mutation rate
POOL_NAME = "green"
FPS = 25

network = Network()
pool = Pool(BOARD_SIZE, MAX_MOVES, network)
pool.load(POOL_NAME)

if(pool.get_size() == 0):
    pool.seed(100)
    pool.race(top=10, games_per_snake=5)

for epoch in range(5):

    Log("--- Epoch #{} ---".format(epoch))

    pool.populate(pool_size=100, alpha = ALPHA)
    snakes, scores = pool.race(top=10, games_per_snake=5)

    for i,score  in enumerate(scores):
        snake = snakes[i]
        Log("Rank #{} - [{}] Gen: {} - Fitness = {}".format(i, snake.get_id(), snake.get_generation(), score))
    
    Log("")

pool.save(POOL_NAME)

#test best snake
snake = pool.get_snakes()[0]
best_game, worst_game = test_snake(snake, number_of_games=100, board_size=BOARD_SIZE, max_moves=MAX_MOVES, predictor=network)

#replay best & worst games
animator = Animator()
animator.animate(best_game, fps=FPS)
animator.animate(worst_game, fps=FPS)


