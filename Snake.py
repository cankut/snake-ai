import numpy as np
import json

class Snake:

    @staticmethod
    def from_file(file):
        with open(file) as json_file:
            data = json.load(json_file)
            c = np.array(data["chromosome"])
            id = str(data["id"])
            generation = int(data["generation"])
            parent_id = data["parent_id"]
            return Snake(id, c, parent_id, generation)

    def __init__(self, id: str, chromosome, parent_id: str, generation: int):
        self.__chromosome = chromosome
        self.__id = id
        self.__parent_id = parent_id
        self.__generation = generation
        pass

    def get_chromosome(self):
        return self.__chromosome

    def get_generation(self):
        return self.__generation

    def get_parent_id(self):
        return self.__parent_id

    def get_id(self):
        return self.__id

    def get_epoch_entry(self, fitness: int):
        entry = {'id': self.__id, 'parent_id': self.__parent_id, 'generation': self.__generation, 'fitness': fitness  }
        return entry

    def save(self, file):
        data = {}
        data["chromosome"] = list(self.__chromosome)
        data["id"] = self.__id
        data["parent_id"] = self.__parent_id
        data["generation"] = self.__generation

        with open(file, 'w') as outfile:
            json.dump(data, outfile)