import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

timesteps = 64

model = keras.Sequential()
model.add(layers.Embedding(input_dim=48, output_dim=128))
model.add(layers.LSTM(128,return_sequences=True,input_shape=(timesteps, 128)))
model.add(layers.LSTM(128))
model.add(layers.Dense(10))

model.compile(optimizer = 'sgd', loss='mse', metrics = ['accuracy'])
es = EarlyStopping(monitor='acc', restore_best_weights = True)
#TODO: uncomment line below once I have access to training data set
#model.fit_generator(train_data_gen, epochs= num_epochs, callbacks = [es])

# Calling `save('my_model.h5')` creates a h5 file `my_model.h5`.
model.save("my_h5_model.h5")