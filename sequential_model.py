from numpy import genfromtxt
from numpy import array
from numpy import reshape
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator


def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return array(dataX), array(dataY)

# Parameters
num_epochs = 10
look_back = 16
lstm_state_size = 64
batch_size = 32
input_location = 'trainingSet8_normalized_65.csv'
label_location = 'trainingSet8_label_65.csv'
train_data_percentage = 0.67


x = genfromtxt(input_location, delimiter=',', skip_header = 1)
y = genfromtxt(label_location, delimiter=',', skip_header = 1)

num_features = x.shape[1]
num_labels = y.shape[1]

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

#This is a simple model that only predicts Chance of trade. 
#A non-sequential model should be used to guess both # and size
model = keras.Sequential()
#model.add(layers.Embedding(input_dim=num_features, output_dim=lstm_state_size))
model.add(layers.LSTM(lstm_state_size, input_shape=(num_features, look_back)))
#model.add(layers.LSTM(lstm_state_size,return_sequences=True,input_shape=(look_back, lstm_state_size)))
#model.add(layers.LSTM(lstm_state_size))
model.add(layers.Dense(num_labels))

model.compile(optimizer = 'sgd', loss='mse', metrics = ['accuracy'])
es = EarlyStopping(monitor='accuracy', restore_best_weights = True)
model.fit(trainX,trainY, epochs= num_epochs, callbacks = [es])

model.save("sequential_model.h5")