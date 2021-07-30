# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 15:32:07 2019

A really simple implementation of Keras functional model

@author: kerem.ataman
"""

from numpy import genfromtxt
from numpy import array
from numpy import reshape
from numpy.random import rand
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
import os

def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return array(dataX), array(dataY)

train_data_percentage = 0.67

num_epochs = 1
lstm_state_size = 64
look_back = 136
# used to be 1 for some bizzare reason
batch_size = 32

num_features = 128
num_instances = look_back * 32
num_labels = 8
x = rand(num_instances,num_features)
y = rand(num_instances,num_labels)

train_size = round(len(x) * train_data_percentage)
train_x = x[0:train_size,:]
train_y = y[0:train_size,:]
test_x = x[train_size:len(x),:]
test_y = y[train_size:len(x),:]
#create train and test sets
#create generators for training and testing data
train_data_gen = TimeseriesGenerator(train_x, train_y,
	length=look_back, sampling_rate=1,stride=1,
    batch_size= batch_size)

test_data_gen = TimeseriesGenerator(test_x, test_y,
	length=look_back, sampling_rate=1,stride=1,
    batch_size= batch_size)

visible = Input(shape=(look_back, num_features))
hidden1 = LSTM(lstm_state_size)(visible)
output = Dense(num_labels)(hidden1)

model = Model(inputs=visible, outputs=output)
model.compile(optimizer = 'sgd', loss='mse', metrics = ['accuracy'])
es = EarlyStopping(monitor='acc', restore_best_weights = True)
model.fit_generator(train_data_gen, epochs= num_epochs, callbacks = [es])

scoreTest = model.evaluate_generator(test_data_gen)

#save model
model.save('quick_and_dirty_model.h5')

print("--------Layer " + "MODEL DETAILS" + "--------")
i = 0
for layer in model.layers:
    print("--------Layer " + str(i) + "--------")
    print("name: " + layer.name)
    print("input shape: " + str(layer.input_shape))
    print("output shape: " + str(layer.output_shape))
    i+=1

print("All Done!")