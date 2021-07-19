# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 15:32:07 2019

A really simple implementation of Keras functional model

@author: kerem.ataman
"""

import pandas as pd
from data.RNNData import OutputName
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.callbacks import EarlyStopping
from keras.layers import Dense, LSTM
from keras.layers import Input
from keras.models import Model

train_data_percentage = 0.67

inputLocation = r'C:\Users\kerem.ataman\Desktop\RTA test\latest\outputName_normalized_1019.csv'
labelLocation = r'C:\Users\kerem.ataman\Desktop\RTA test\latest\outputName_label_1019.csv'
rawLocation =  r'C:\Users\kerem.ataman\Desktop\RTA test\latest\outputName_1019.csv'
newsLocation = r"C:\Users\kerem.ataman\Documents\news\news_archive.csv"

#symbols_to_use = None
symbols_to_use = ['USDCAD']

helper = OutputName(pd.read_csv(inputLocation), pd.read_csv(labelLocation), None, None)
helper.dropNanCols()

num_epochs = 10
lstm_state_size = 64
look_back = 8
batch_size = 1

[x, y] = helper.toNumpyArrays()

num_features = x.shape[1]
num_labels = y.shape[1]

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
model.save('Customer1019DataModel.h5')