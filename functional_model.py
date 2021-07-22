# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 15:32:07 2019

A really simple implementation of Keras functional model

@author: kerem.ataman
"""

from numpy import genfromtxt
from numpy import array
from numpy import reshape
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

inputLocation = 'trainingSet8_normalized_65.csv'
labelLocation = 'trainingSet8_label_65.csv'
num_epochs = 10
lstm_state_size = 64
look_back = 8
# used to be 1 for some bizzare reason
batch_size = 32

#TODO: line below, proper
#x = genfromtxt(os.getcwd()+'/'+inputLocation, delimiter=',', skip_header = 1)
x = genfromtxt(inputLocation, delimiter=',', skip_header = 1)
y = genfromtxt(os.getcwd()+'/'+labelLocation, delimiter=',', skip_header = 1)

print(len(x))
num_features = x.shape[1]
num_labels = y.shape[1]

# train_size = round(len(x) * train_data_percentage)
# train_x = x[0:train_size,:]
# train_y = y[0:train_size,:]
# test_x = x[train_size:len(x),:]
# test_y = y[train_size:len(x),:]
# #create train and test sets
# #create generators for training and testing data
# train_data_gen = TimeseriesGenerator(train_x, train_y,
# 	length=look_back, sampling_rate=1,stride=1,
#     batch_size= batch_size)

# test_data_gen = TimeseriesGenerator(test_x, test_y,
# 	length=look_back, sampling_rate=1,stride=1,
#     batch_size= batch_size)

train_size = round(len(x) * train_data_percentage)
train_x = x[0:train_size,:]
train_y = y[0:train_size,:]
test_x = x[train_size:len(x),:]
test_y = y[train_size:len(x),:]
trainX, trainY = create_dataset(x, look_back)
# reshape input to be [samples, time steps, features]
trainX = reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
testX, testY = create_dataset(y, look_back)
testX = reshape(testX, (testX.shape[0], 1, testX.shape[1]))

visible = Input(shape=(num_features,look_back))
hidden1 = LSTM(lstm_state_size)(visible)
output = Dense(num_labels)(hidden1)
#TODO: later, add two output layers like
#output2 = Dense(x)(y)
#model = Model(inputs=visible, outputs=[output,output2])

model = Model(inputs=visible, outputs=output)
model.compile(optimizer = 'sgd', loss='mse', metrics = ['accuracy'])
es = EarlyStopping(monitor='accuracy', restore_best_weights = True)
#model.fit_generator(train_data_gen, epochs= num_epochs, callbacks = [es])
model.fit(trainX,trainY, epochs= num_epochs, callbacks = [es])

#scoreTest = model.evaluate_generator(test_data_gen)

#save model
model.save('functional_model.h5')