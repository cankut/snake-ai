from Snake import Snake
import numpy as np
from Common import generate_id

class Genetics:

    @staticmethod
    def mutate(chromosome, alpha):
        n = len(chromosome)
        delta = np.random.uniform(-alpha, alpha, n) # draw samples from uniform distribution
        m = chromosome + delta # mutate chromosome adding delta values
        return m

    @staticmethod
    def reproduce(snake: Snake, child_count, alpha):
        children = []
        for _ in range(child_count):
            c = snake.get_chromosome()
            m = Genetics.mutate(c, alpha)

            id = generate_id()
            parent_id = snake.get_id()
            generation = snake.get_generation()
            
            children.append(Snake(id, m,parent_id, generation+1))

        return children