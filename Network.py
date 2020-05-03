import keras
from keras.layers import Dense
from keras.models import Sequential
import numpy as np

class Network:

    def __init__(self):
        
        initializer = keras.initializers.random_normal(mean=0,stddev=0.1)
        model = Sequential()
        model.add(Dense(units=3, activation='linear', input_dim=6, kernel_initializer=initializer, bias_initializer=initializer))
    
        self.__model = model
    
    def get_parameter_count(self):
        model = self.__model
        trainable_count = keras.utils.layer_utils.count_params(model.trainable_weights)
        return trainable_count

    def get_layer_sizes(self):
        n_layers = []
        model = self.__model
        n_input = model.layers[0].input_shape[1]
        n_layers.append(n_input)

        for l in model.layers:
            n_l = l.output_shape[1]
            n_layers.append(n_l)

        return n_layers

    def load(self, chromosome):

        n_layers = self.get_layer_sizes()

        for l in range(len(n_layers)-1):

            n, n_next = n_layers[l],n_layers[l+1]

            n_weight = n * n_next
            n_bias = n_next
            n_total = n_weight + n_bias

            layer_params = chromosome[:n_total]

            w = layer_params[:n_weight]
            b = layer_params[n_weight:]

            weights = [np.array(w).reshape(n,n_next), np.array(b).reshape(n_next,)]

            self.__model.layers[l].set_weights(weights)
            chromosome = chromosome[n_total:]

    def predict(self, inputs):
        inputs = np.array(inputs).reshape(1,-1)
        result = self.__model.predict(inputs)[0]
        i = np.argmax(result)
        return i
