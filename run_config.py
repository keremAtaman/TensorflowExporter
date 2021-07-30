from enum import Enum, auto
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import metrics

#FIXME LATER: convert this into JSON or Python dict

class FROM_AND_TO_DATE_DETERMINATION(Enum):
    SET_MANUALLY = auto()
    USE_TRADE_DATES_AND_PERCENTAGES = auto()

# TODO: use the below
class EVENT_TYPE(Enum):
    ccypos = auto()
    cs = auto()
    login = auto()
    panel = auto()
    pos = auto()
    transaction = auto()

class RunConfig():
    class DataConfig():
        output_folder = 'outputs'
        # =================================== IN CASE DATA EXISTS AS CSV, THEIR LOCATIONS ======================================================
        # TODO: from and to times etc
        def get_csv_filename(
            rqstr_party_id : int,
            from_timestamp:str,
            to_timestamp:str,
            is_input: bool = True,
            is_training: bool = True,
            label_time_interval:str = "",
        ) -> str:
            """creates the csv filename for the data with the given parameters.

            Args:
                rqstr_party_id (int): party_id of the customer for which data is being acquired
                from_timestsamp (str): the fromTimestamp of data (when the data begins)
                to_timestsamp (str): the toTimestamp of data (when the data ends)
                is_input (bool, optional): Defines whether the data is for input or label (output). Set to True if the data is input. Defaults to True.
                is_training (bool, optional): Defines whether the data is for training or testing. Set to True if the data is for training.  Defaults to True.
                label_time_interval (str, optional): The time interval for label (how often label is generated). e.g. '24 hours'.  Only used when is_training = False. Defaults to \"\".
            Returns:
                str: the csv file name
            """
            input_or_label = "input"
            if not is_input:
                input_or_label = "label"
            
            train_or_test = "train"
            if not is_training:
                train_or_test = "test" + label_time_interval
            
            return RunConfig.DataConfig.output_folder + "/" + str(rqstr_party_id) + "_" + input_or_label + "_" + train_or_test + from_timestamp + "_" + to_timestamp
        # =================================== DATABASE CONFIGS ==========================================================================
        database_config_location = 'database/credentials.json'
        # =================================== DATA CONFIGS ==============================================================================
        # The first ctpty is the one that will be used for training, removing cols etc
        rqstr_party_id_list = [27]
        event_list = ['ccypos','cs','login','panel','pos','transaction']
        ccy_pair_list = ['USDCAD','EURUSD','EURCAD','GBPUSD'] 
        # what should be the distance between intervals be 
        label_time_interval = '24 hours'
        #label_time_interval = '1 hours'
        label_starting_time = '00:00:00'
        # TODO: use the enum below
        from_and_to_date_determination = FROM_AND_TO_DATE_DETERMINATION.USE_TRADE_DATES_AND_PERCENTAGES
        # =================== The below will only be used if time_range_determination_method is set to "SET_MANUALLY"=================== 
        training_data_from_timestamp = '2020-01-01 00:00:00'
        training_data_to_timestamp = '2020-01-20 23:59:59'
        testing_data_from_timestamp = '2020-02-01 00:00:00'
        testing_data_to_timestamp = '2020-02-03 23:59:59'
        # ==============================================================================================================================
        # =================== The below will only be used if time_range_determination_method is set to USE_TRADE_DATES_AND_PERCENTAGES =================== 
        # determines what percentage of the data should be used for training. 1 is for 100% (using all data for training), 0.5 is for 50% etc
        training_percentage = 0.67
        # ================================================================================================================================================ 

    # =================================== NN CONFIGS ==============================================================================
    class NNConfig():
        look_back = 64
        epochs = 100
        lstm_state_size = 128
        batch_size = 32
        # optimizer for the nn
        optimizer = 'sgd'
        # how to calculate loss
        loss = 'mse'
        # metrics to track during model fitting
        #metrics = [metrics.Precision(),metrics.Accuracy(),metrics.Recall()]
        metrics = ['accuracy']
        #es = EarlyStopping(monitor='accuracy', restore_best_weights = True, patience = 3)
        callbacks = [
            EarlyStopping(monitor='accuracy', restore_best_weights = True, patience = 5)
        ]
    
