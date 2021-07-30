from run_config import RunConfig as rc
from data.from_and_to_date_determination import from_and_to_date_determination
from data.data_handler import CustomerDataHandler 
import data_helper as dh

def work():
    # handle from and to dates
    [
        training_data_from_timestamp,
        training_data_to_timestamp,
        testing_data_from_timestamp,
        testing_data_to_timestamp
    ] = from_and_to_date_determination()
    outputs = {}
    dropped_cols = None

    #generate data for each customer
    for rqstr_party_id in rc.DataConfig.rqstr_party_id_list:
        outputs[rqstr_party_id] = {}
        #FIXME: there is no test dataset for party_ids after the first one. Make this more configurable
        if rqstr_party_id != rc.DataConfig.rqstr_party_id_list[0]:
            training_data_to_timestamp = testing_data_to_timestamp
        input_csv = rc.DataConfig.get_csv_filename(rqstr_party_id,
                                                        is_input= True,
                                                        is_training = True,
                                                        label_time_interval=rc.DataConfig.label_time_interval,
                                                        from_timestamp = training_data_from_timestamp,
                                                        to_timestamp = training_data_to_timestamp)
        label_csv = rc.DataConfig.get_csv_filename(rqstr_party_id,
                                                        is_input= False,
                                                        is_training = True,
                                                        label_time_interval=rc.DataConfig.label_time_interval,
                                                        from_timestamp = training_data_from_timestamp,
                                                        to_timestamp = training_data_to_timestamp)
        #create training dataset 
        cdh = CustomerDataHandler(
            rqstr_party_id = rqstr_party_id,
            event_list = rc.DataConfig.event_list,
            ccy_pair_list = rc.DataConfig.ccy_pair_list,
            from_timestamp = training_data_from_timestamp,
            to_timestamp = training_data_to_timestamp,
            label_starting_time = rc.DataConfig.label_starting_time,
            label_time_interval = rc.DataConfig.label_time_interval,
            connection_credentials = rc.DataConfig.database_config_location,
            input_csv = input_csv,
            label_csv = label_csv
        )
        [train_x_df,train_y_df] = cdh.work()
        train_x_df.to_csv(input_csv)
        train_y_df.to_csv(label_csv)
        [train_x,train_y,dropped_cols] = dh.create_input_and_output_arrays_for_nn(train_x_df,train_y_df,rc.NNConfig.look_back,dropped_cols)
        outputs[rqstr_party_id]['train'] = [train_x,train_y,dropped_cols]


        #create testing dataset
        input_csv = rc.DataConfig.get_csv_filename(rqstr_party_id,
                                                    is_input= True,
                                                    is_training = False,
                                                    label_time_interval=rc.DataConfig.label_time_interval,
                                                    from_timestamp = testing_data_from_timestamp,
                                                    to_timestamp = testing_data_to_timestamp)
        label_csv = rc.DataConfig.get_csv_filename(rqstr_party_id,
                                                            is_input= False,
                                                            is_training = False,
                                                            label_time_interval=rc.DataConfig.label_time_interval,
                                                            from_timestamp = testing_data_from_timestamp,
                                                            to_timestamp = testing_data_to_timestamp)
        if rqstr_party_id == rc.DataConfig.rqstr_party_id_list[0]:
            cdh = CustomerDataHandler(
                rqstr_party_id = rqstr_party_id,
                event_list = rc.DataConfig.event_list,
                ccy_pair_list = rc.DataConfig.ccy_pair_list,
                from_timestamp = testing_data_from_timestamp,
                to_timestamp = testing_data_to_timestamp,
                label_starting_time = rc.DataConfig.label_starting_time,
                label_time_interval = rc.DataConfig.label_time_interval,
                connection_credentials = rc.DataConfig.database_config_location,
                input_csv = input_csv,
                label_csv = label_csv)

            [test_x_df,test_y_df] = cdh.work()
            test_x_df.to_csv(input_csv)
            test_y_df.to_csv(label_csv)
            [test_x,test_y,dropped_cols] = dh.create_input_and_output_arrays_for_nn(test_x_df,test_y_df,rc.NNConfig.look_back,dropped_cols)
            outputs[rqstr_party_id]['test'] = [test_x,test_y,dropped_cols]
        else:
            #FIXME: there is no test dataset for party_ids after the first one. Make this more configurable
            outputs[rqstr_party_id]['test'] = [[],[],dropped_cols]
        
    return outputs

