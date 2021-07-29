from data.data_handler import CustomerDataHandler 
import pandas as pd
import data_helper as dh
from numpy import reshape
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model

#TODO LATER: move data reshaping to somewhere else
#TODO LATER: move neural net creation to somewhere else

#TODO: deal with input and output sizes being unequal
#TODO: training and testing datasets. They need to be acquired seperately

#One sequence is one sample. A batch is comprised of one or more samples
look_back = 16
train_data_percentage = 0.67

# =================== generate customer train data ===================
cdh = CustomerDataHandler(from_timestamp='2020-01-01 00:00:00',
                             to_timestamp = '2020-09-30 08:59:59',
                             label_from_timestamp = '2020-01-01 00:00:00',
                             label_to_timestamp = '2020-09-30 23:59:00') 
[train_x_df,train_y_df] = cdh.work()
train_x_df.to_csv('741_train_x.csv')
train_y_df.to_csv('741_train_y.csv')
# =================== Use Existing Data ===================
# train_x_df = pd.read_csv('741_train_x.csv', index_col=[0])
# train_y_df = pd.read_csv('741_train_y.csv', index_col=[0])
# train_x_df['event_ts'] = pd.to_datetime(train_x_df.event_ts)
# train_y_df['event_ts'] = pd.to_datetime(train_y_df.event_ts)
# =========================================================
[train_x,train_y,dropped_cols] = dh.create_input_and_output_arrays_for_nn(train_x_df,train_y_df,look_back,None)
num_features = train_x.shape[2]
num_labels = train_y.shape[1]

# =================== generate customer test data ===================
cdh = CustomerDataHandler(from_timestamp='2020-10-01 00:00:00',
                             to_timestamp = '2020-12-30 08:59:59',
                             label_from_timestamp = '2020-10-01 00:00:00',
                             label_to_timestamp = '2020-12-30 23:59:00') 
[test_x_df,test_y_df] = cdh.work()
test_x_df.to_csv('741_test_x.csv')
test_y_df.to_csv('741_test_y.csv')
# =================== Use Existing Data ===================
# test_x_df = pd.read_csv('741_test_x.csv', index_col=[0])
# test_y_df = pd.read_csv('741_test_y.csv', index_col=[0])
# test_x_df['event_ts'] = pd.to_datetime(test_x_df.event_ts)
# test_y_df['event_ts'] = pd.to_datetime(test_y_df.event_ts)
# =========================================================
[test_x,test_y,dropped_cols] = dh.create_input_and_output_arrays_for_nn(test_x_df,test_y_df,look_back,dropped_cols)

#define nn
num_epochs = 100
# num steps before a model is updated 
batch_size = train_x.shape[0]
test_batch_size = test_x.shape[0]
lstm_state_size = 64
visible = Input(shape=(look_back,num_features))
hidden1 = LSTM(lstm_state_size)(visible)
output = Dense(num_labels)(hidden1)
model = Model(inputs=visible, outputs=output)
model.compile(optimizer = 'sgd', loss='mse', metrics = ['accuracy','mse'])
#monitor = 'loss' is also available
es = EarlyStopping(monitor='accuracy', restore_best_weights = True, patience = 3)
model.fit(train_x,train_y, epochs= num_epochs, callbacks = [es])
# model.fit(train_x,train_y, epochs= num_epochs)

if len(test_x)>0:
    print("=========================testing=========================")
    results = model.evaluate(test_x,test_y,test_batch_size)

#save model
model.save('functional_model.h5')

print("All Done!")