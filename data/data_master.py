from run_config import RunConfig as rc
from data.from_and_to_date_determination import from_and_to_date_determination
from data.data_handler import CustomerDataHandler 
import data_helper as dh
import pandas as pd

# TODO: normalize test with the same variables used for train

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

        input_csv = rc.DataConfig.get_filename_base(rqstr_party_id,
                                                        from_timestamp = training_data_from_timestamp,
                                                        to_timestamp = training_data_to_timestamp,
                                                        is_input= True,
                                                        is_training = True,
                                                        label_time_interval=rc.DataConfig.label_time_interval
                                                        ) + '.csv'
        label_csv = rc.DataConfig.get_filename_base(rqstr_party_id,
                                                        from_timestamp = training_data_from_timestamp,
                                                        to_timestamp = training_data_to_timestamp,
                                                        is_input= False,
                                                        is_training = True,
                                                        label_time_interval=rc.DataConfig.label_time_interval
                                                        ) + '.csv'
        #create training dataset 
        cdh = CustomerDataHandler(
            rqstr_party_id = rqstr_party_id,
            trade_state_cd_list = rc.DataConfig.trade_state_cd_list,
            buy_sell_action_cd_list = rc.DataConfig.buy_sell_action_cd_list,
            event_list = rc.DataConfig.event_list,
            ccy_pair_list = rc.DataConfig.ccy_pair_list,
            from_timestamp = training_data_from_timestamp,
            to_timestamp = training_data_to_timestamp,
            label_starting_time = rc.DataConfig.label_starting_time,
            label_time_interval = rc.DataConfig.label_time_interval,
            connection_credentials = rc.DataConfig.database_config_location,
            input_csv = input_csv,
            label_csv = label_csv,
            cs_period_multiplier = rc.DataConfig.cs_period_multiplier,
            cs_period_unit_cd = rc.DataConfig.cs_period_unit_cd
        )
        [train_x_df,train_y_df] = cdh.work()
        train_x_df.to_csv(input_csv)
        train_y_df.to_csv(label_csv)
        train_artifacts = dh.create_input_and_output_arrays_for_nn(train_x_df,train_y_df,rc.NNConfig.look_back,dropped_cols)
        # TODO: there is no reason for "train" prefix considering we are in [rqstr_party_id]['train'] area of the dict. Remove the prefix from here and main.py
        outputs[rqstr_party_id]['train'] = {
            'x_df': train_x_df,
            'x':train_artifacts['train_x'],
            'x_mean':train_artifacts['train_x_mean'],
            'x_std':train_artifacts['train_x_std'],
            'y_df': train_y_df,
            'y':train_artifacts['train_y'],
            'y_mean':train_artifacts['train_y_mean'],
            'y_std':train_artifacts['train_y_std'],
            'dropped_cols':train_artifacts['dropped_input_cols']}


        #create testing dataset
        input_csv = rc.DataConfig.get_filename_base(rqstr_party_id,
                                                    from_timestamp = testing_data_from_timestamp,
                                                    to_timestamp = testing_data_to_timestamp,
                                                    is_input= True,
                                                    is_training = False,
                                                    label_time_interval=rc.DataConfig.label_time_interval) + '.csv'
        label_csv = rc.DataConfig.get_filename_base(rqstr_party_id,
                                                            from_timestamp = testing_data_from_timestamp,
                                                            to_timestamp = testing_data_to_timestamp,
                                                            is_input= False,
                                                            is_training = False,
                                                            label_time_interval=rc.DataConfig.label_time_interval
                                                            ) + '.csv'
        if rqstr_party_id == rc.DataConfig.rqstr_party_id_list[0]:
            cdh = CustomerDataHandler(
                rqstr_party_id = rqstr_party_id,
                trade_state_cd_list = rc.DataConfig.trade_state_cd_list,
                buy_sell_action_cd_list = rc.DataConfig.buy_sell_action_cd_list,
                event_list = rc.DataConfig.event_list,
                ccy_pair_list = rc.DataConfig.ccy_pair_list,
                from_timestamp = testing_data_from_timestamp,
                to_timestamp = testing_data_to_timestamp,
                label_starting_time = rc.DataConfig.label_starting_time,
                label_time_interval = rc.DataConfig.label_time_interval,
                connection_credentials = rc.DataConfig.database_config_location,
                input_csv = input_csv,
                label_csv = label_csv,
                cs_period_multiplier = rc.DataConfig.cs_period_multiplier,
                cs_period_unit_cd = rc.DataConfig.cs_period_unit_cd)

            [test_x_df,test_y_df] = cdh.work()
            test_x_df.to_csv(input_csv)
            test_y_df.to_csv(label_csv)
            test_artifacts = dh.create_input_and_output_arrays_for_nn(
                test_x_df,
                test_y_df,
                rc.NNConfig.look_back,
                dropped_cols,
                train_artifacts['train_x_mean'],
                train_artifacts['train_x_std'],
                train_artifacts['train_y_mean'],
                train_artifacts['train_y_std'],
                )
            # TODO: there is no reason for "test" prefix considering we are in [rqstr_party_id]['test'] area of the dict. Remove the prefix from here and main.py
            outputs[rqstr_party_id]['test'] = {
                'x_df':test_x_df,
                'x':test_artifacts['train_x'],
                'x_mean':test_artifacts['train_x_mean'],
                'x_std':test_artifacts['train_x_std'],
                'y_df':test_y_df,
                'y':test_artifacts['train_y'],
                'y_mean':test_artifacts['train_y_mean'],
                'y_std':test_artifacts['train_y_std'],
                'dropped_cols':test_artifacts['dropped_input_cols']}
        # FIXME: currently, if this is not the 1st ctpty in the list, we leave the "test" section empty and use "train" to evaluate model. We should leave "train" empty and use test instead
        else:
            # TODO: there is no reason for "test" prefix considering we are in [rqstr_party_id]['test'] area of the dict. Remove the prefix from here and main.py
            outputs[rqstr_party_id]['test'] = {
                'x':None,
                'y':None,
                'dropped_cols':dropped_cols}
        
    return outputs

