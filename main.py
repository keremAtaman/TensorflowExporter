from data.data_handler import CustomerDataHandler 
import pandas as pd
import data_helper as dh
from numpy import reshape
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from run_config import RunConfig as rc
from data import data_master as dm
import pickle

#TODO LATER: move data reshaping to somewhere else
#TODO LATER: move neural net creation to somewhere else
# TODO LATER: multithreading

# =================== generate customer train data ===================
outputs = dm.work()

model = None
num_features = outputs[rc.DataConfig.rqstr_party_id_list[0]]['train'][0].shape[2]
num_labels = outputs[rc.DataConfig.rqstr_party_id_list[0]]['train'][1].shape[1]
results = {}
for rqstr_party_id in outputs:
    train_x = outputs[rqstr_party_id]['train'][0]
    train_y = outputs[rqstr_party_id]['train'][1]
    test_x = outputs[rqstr_party_id]['test'][0]
    test_y = outputs[rqstr_party_id]['test'][1]
    # num steps before a model is updated 
    #batch_size = train_x.shape[0]
    batch_size = rc.NNConfig.batch_size
    #train the model using a single ctpty
    if rqstr_party_id == rc.DataConfig.rqstr_party_id_list[0]:
        visible = Input(shape=(rc.NNConfig.look_back,num_features))
        hidden1 = LSTM(rc.NNConfig.lstm_state_size)(visible)
        output = Dense(num_labels)(hidden1)
        model = Model(inputs=visible, outputs=output)
        model.compile(optimizer = rc.NNConfig.optimizer, loss=rc.NNConfig.loss, metrics = rc.NNConfig.metrics)
        #monitor = 'loss' is also available
        model.fit(train_x,train_y, epochs= rc.NNConfig.epochs, callbacks = rc.NNConfig.callbacks)
        # model.fit(train_x,train_y, epochs= num_epochs)

        if len(test_x)>0:
            print("=========================testing " +str(rqstr_party_id) + "=========================")
            results[rqstr_party_id] = model.evaluate(test_x,test_y,batch_size)
            print("==================================================")
    
    else:
        print("=========================testing " +str(rqstr_party_id) + "=========================")
        results[rqstr_party_id] = model.evaluate(train_x,train_y,batch_size)
        print("==================================================")


#save model
model.save('functional_model.h5')

#TODO: pickle/write out the results and config with naming similar to csv file format ()
# results is in form [loss,accuracy]
print(results)
# pickle.dump( [], open( "save.p", "wb" ) )

#print out model details
print("--------Layer " + "MODEL DETAILS" + "--------")
i = 0
for layer in model.layers:
    print("--------Layer " + str(i) + "--------")
    print("name: " + layer.name)
    print("input shape: " + str(layer.input_shape))
    print("output shape: " + str(layer.output_shape))
    i+=1

print("All Done!")