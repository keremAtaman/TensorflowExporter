from data.data_handler import CustomerDataHandler 
import pandas as pd
import data_helper as dh
from numpy import reshape
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from run_config import RunConfig as rc
from run_config import COLUMN_TYPE as CT
from data import data_master as dm
from reporting import prediction_formatter as pf
import pickle

# TODO: handling of periodicity
# TODO: saving mean and stdev normalizers somewhere

#TODO LATER: move data reshaping to somewhere else
#TODO LATER: move neural net creation to somewhere else
# TODO LATER: multithreading
# TODO LATER: ability to use ARIMA m periodicity analysis etc. instead of nn if it goes sour
# =================== generate customer train data ===================
outputs = dm.work()

model = None
num_features = outputs[rc.DataConfig.rqstr_party_id_list[0]]['train']['x'].shape[2]
num_labels = outputs[rc.DataConfig.rqstr_party_id_list[0]]['train']['y'].shape[1]
results = {}
for rqstr_party_id in outputs:
    results[rqstr_party_id] = {}
    train_x = outputs[rqstr_party_id]['train']['x']
    train_y = outputs[rqstr_party_id]['train']['y']
    test_x = outputs[rqstr_party_id]['test']['x']
    test_y = outputs[rqstr_party_id]['test']['y']
    # num steps before a model is updated 
    #batch_size = train_x.shape[0]
    batch_size = rc.NNConfig.batch_size
    #train the model using a single ctpty
    if rqstr_party_id == rc.DataConfig.rqstr_party_id_list[0]:
        visible = Input(shape=(rc.NNConfig.look_back,num_features))
        hidden1 = LSTM(rc.NNConfig.lstm_state_size)(visible)
        output = Dense(num_labels)(hidden1)
        model = Model(inputs=visible, outputs=output)
        model.compile(
            optimizer = rc.NNConfig.optimizer, 
            loss=rc.NNConfig.loss, 
            metrics = rc.NNConfig.metrics)
        model.fit(
            train_x,
            train_y, 
            epochs= rc.NNConfig.epochs, 
            callbacks = rc.NNConfig.callbacks)

        if len(test_x)>0:
            # TODO: check the contents of test_x,test_y etc., make sure they have different cols
            print("=========================testing " +str(rqstr_party_id) + "=========================")
            results[rqstr_party_id]['evaluation'] = model.evaluate(test_x,test_y,batch_size)
            results[rqstr_party_id]['prediction'] = model.predict(test_x)
            print("==================================================")
    
    # TODO: the "test" section should be used instead of "train" - it is confusing
    else:
        print("=========================testing " +str(rqstr_party_id) + "=========================")
        results[rqstr_party_id]['evaluation'] = model.evaluate(train_x,train_y,batch_size)
        results[rqstr_party_id]['prediction'] = model.predict(train_x)
        print("==================================================")

    # FIXME: feeding of column names, types, mean and stdev is so crass
    results[rqstr_party_id]['prediction'] = pf.work(
        results[rqstr_party_id]['prediction'],
        [
            "USDCAD_is_buy",
            "USDCAD_buy_volumebase",
            "USDCAD_is_sell",
            "USDCAD_sell_volumebase",
            "EURCAD_is_buy",
            "EURCAD_buy_volumebase",
            "EURCAD_is_sell",
            "EURCAD_sell_volumebase",
            "GBPUSD_is_buy",
            "GBPUSD_buy_volumebase",
            "GBPUSD_is_sell",
            "GBPUSD_sell_volumebase",
            "EURUSD_is_buy",
            "EURUSD_buy_volumebase",
            "EURUSD_is_sell",
            "EURUSD_sell_volumebase"
        ],
        [
            CT.CATEGORICAL,
            CT.NON_NEGATIVE_NUMERICAL,
            CT.CATEGORICAL,
            CT.NON_NEGATIVE_NUMERICAL,
            CT.CATEGORICAL,
            CT.NON_NEGATIVE_NUMERICAL,
            CT.CATEGORICAL,
            CT.NON_NEGATIVE_NUMERICAL,
            CT.CATEGORICAL,
            CT.NON_NEGATIVE_NUMERICAL,
            CT.CATEGORICAL,
            CT.NON_NEGATIVE_NUMERICAL,
            CT.CATEGORICAL,
            CT.NON_NEGATIVE_NUMERICAL,
            CT.CATEGORICAL,
            CT.NON_NEGATIVE_NUMERICAL
        ],
        outputs[rqstr_party_id]['train']['y_mean'],
        outputs[rqstr_party_id]['train']['y_std']
    )

    predictions = pd.DataFrame(results[rqstr_party_id]['prediction'])
    #TODO: function to generate the name as below
    predictions.to_csv('outputs/predictions_' + str(rqstr_party_id) + '.csv')

    # TODO: now that prediction results are saved, get predicted vs actual, unnormalized
    
    # FIXME: label names needs to not be static
    # TODO: create [<prediction/label>][ccy_pair][<num/volume>]
    # TODO: get last 3 months' avg
    # predictions_and_results = data_merger.work(
    #     results[rqstr_party_id]['prediction'],
    #     outputs[rqstr_party_id]['test']['test_x_mean'],
    #     outputs[rqstr_party_id]['test']['test_x_std'],
    #     prediction_titles,
    #     test_y,
    #     outputs[rqstr_party_id]['test']['test_x_mean'],
    #     outputs[rqstr_party_id]['test']['test_x_std'],
    #     label_titles
    # )

    # TODO: convert these into something workable by prediction_writer

#save model
model.save('functional_model.h5')

#TODO: pickle/write out the results and config with naming similar to csv file format ()
# results is in form [loss,accuracy]
pickle.dump(results, open( "outputs/results.pkl", "wb" ), protocol=pickle.HIGHEST_PROTOCOL)
# to retrieve: results = pickle.load(open( "outputs/results.pkl", "rb" ))

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