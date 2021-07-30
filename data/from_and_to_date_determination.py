from run_config import RunConfig as rc
from run_config import FROM_AND_TO_DATE_DETERMINATION
from database.database_handler import get_connection
from datetime import timedelta 
import pandas as pd

#FIXME: have the config file as input instead of comping it


def from_and_to_date_determination():
    training_data_from_timestamp = None
    training_data_to_timestamp = None
    testing_data_from_timestamp = None
    testing_data_to_timestamp = None

    if rc.DataConfig.from_and_to_date_determination == FROM_AND_TO_DATE_DETERMINATION.SET_MANUALLY:
        training_data_from_timestamp = rc.DataConfig.training_data_from_timestamp
        training_data_to_timestamp = rc.DataConfig.training_data_to_timestamp
        testing_data_from_timestamp = rc.DataConfig.testing_data_from_timestamp
        testing_data_to_timestamp = rc.DataConfig.testing_data_to_timestamp
    elif rc.DataConfig.from_and_to_date_determination == FROM_AND_TO_DATE_DETERMINATION.USE_TRADE_DATES_AND_PERCENTAGES:
        conn = get_connection(rc.DataConfig.database_config_location)
        with open('database/'+'get_min_and_max_trade_done_dates'+'.sql','r') as file:
                sql_query = file.read()
        ccy_pair_list_ = str(rc.DataConfig.ccy_pair_list)
        ccy_pair_list_ = ccy_pair_list_.replace("[","(")
        ccy_pair_list_ = ccy_pair_list_.replace("]",")")
        sql_query = sql_query.replace(r'$P{ccy_pair_list}',ccy_pair_list_)
        rqstr_party_id_list_ = "("
        for rqstr_party_id in rc.DataConfig.rqstr_party_id_list:
            rqstr_party_id_list_ += str(rqstr_party_id) + ","
        rqstr_party_id_list_ = rqstr_party_id_list_[:-1]
        rqstr_party_id_list_ += ")"
        #rc.DataConfig.rqstr_party_id_list
        sql_query = sql_query.replace(r'$P{rqstr_party_id_list}',rqstr_party_id_list_)
        df = pd.read_sql(sql_query,conn,parse_dates={'earliestDate':'%y-%m-%d %H:%M:%S','latestDate':'%y-%m-%d %H:%M:%S'})

        training_data_from_timestamp_ = df.iloc[0]['earliestdate']
        num_days_to_add = int(df.iloc[0]['day_difference'] * rc.DataConfig.training_percentage)
        training_data_to_timestamp_ = training_data_from_timestamp_ + timedelta(days = num_days_to_add)
        testing_data_from_timestamp_ = training_data_to_timestamp_ + timedelta(days = 1)
        testing_data_to_timestamp_ = df.iloc[0]['latestdate']

        training_data_from_timestamp = str(training_data_from_timestamp_)
        training_data_to_timestamp = str(training_data_to_timestamp_)
        testing_data_from_timestamp = str(testing_data_from_timestamp_)
        testing_data_to_timestamp = str(testing_data_to_timestamp_)
    return [
        training_data_from_timestamp,
        training_data_to_timestamp,
        testing_data_from_timestamp,
        testing_data_to_timestamp
    ] 