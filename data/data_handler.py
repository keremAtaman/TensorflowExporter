#TODO LATER: enumerate event_type
#TODO LATER: somehow tell the algo that events happened X hours before predictions. Maybe num_days_since_last_activity?
#TODO LATER: data processing takes too long
#TODO LATER: enum'd column names, ability to select which columns (as well as events) to calculate

import pandas as pd
import database.database_handler as dh
from data.events.ccypos_event_handler import CcyPosEventHandler as CPEH
from data.events.cs_event_handler import CsEventHandler as CSEH
from data.events.login_event_handler import LoginEventHandler as LEH
from data.events.panel_event_handler import PanelEventHandler as PEH
from data.events.pos_event_handler import PosEventHandler as PosEH
from data.events.transaction_event_handler import TransactionEventHandler as TEH
from data.events.date_event_handler import DateEventHandler as DEH
from typing import List
import os
import run_config as rc


class CustomerDataHandler:
    #TODO LATER: ability to change ccy_pair_list based on query (watch out for input_row object, that will need to be changed as well!)
    # TODO LATER: there is no need for __init__ - just feed every necessary thing and do the below in work() function
    def __init__(self, rqstr_party_id,
                trade_state_cd_list:List[str],
                buy_sell_action_cd_list:List[str] = ['B','S','BS','SB'],
                event_list: list(rc.EVENT_TYPE) = [rc.EVENT_TYPE.ccypos,
                                                    rc.EVENT_TYPE.cs,
                                                    rc.EVENT_TYPE.login,
                                                    rc.EVENT_TYPE.panel,
                                                    rc.EVENT_TYPE.pos,
                                                    rc.EVENT_TYPE.transaction],
                ccy_pair_list = ['USDCAD','EURUSD','EURCAD','GBPUSD'],
                from_timestamp = '2020-01-01 00:00:00',
                to_timestamp = '2020-01-07 08:59:59',
                label_starting_time = '09:00:00',
                label_time_interval='24 hours',
                connection_credentials = 'database/credentials.json',
                input_csv = None,
                label_csv = None,
                cs_period_multiplier:str = '1',
                cs_period_unit_cd:str = 'h'):
        
        self.rqstr_party_id = rqstr_party_id
        self.event_list = event_list
        self.ccy_pair_list = ccy_pair_list
        self.from_timestamp = from_timestamp
        self.to_timestamp = to_timestamp
        self.label_starting_time = label_starting_time
        self.label_time_interval = label_time_interval
        self.connection_credentials = connection_credentials
        self.input_csv = input_csv
        self.label_csv = label_csv
        self.cs_period_multiplier = cs_period_multiplier
        self.cs_period_unit_cd = cs_period_unit_cd

        self.ccy_list = set()
        for ccy_pair in ccy_pair_list:
            self.ccy_list.add(ccy_pair[0:3])
            self.ccy_list.add(ccy_pair[3:6])
        self.label_from_timestamp = from_timestamp[:-8] + self.label_starting_time

        #initialize handlers, go through the list of things to add
        for event in event_list:
            if event == rc.EVENT_TYPE.ccypos:
                self.ccy_pos_handler = CPEH(self.ccy_list)
            if event == rc.EVENT_TYPE.cs:
                self.cs_handler = CSEH(self.ccy_pair_list,self.cs_period_multiplier,self.cs_period_unit_cd)
            if event == rc.EVENT_TYPE.login:
                self.login_event_handler = LEH()
            if event == rc.EVENT_TYPE.panel:
                self.panel_event_handler = PEH()
            if event == rc.EVENT_TYPE.pos:
                self.pos_event_handler = PosEH(self.ccy_pair_list)
            if event == rc.EVENT_TYPE.transaction:
                self.transaction_event_handler = TEH(
                                            trade_state_cd_list,
                                            buy_sell_action_cd_list,
                                            self.ccy_pair_list
                )
            if event == rc.EVENT_TYPE.date:
                self.date_event_handler = DEH()


    def work(self):
        conn = None

        #get label 
        if (os.path.exists(self.label_csv)):
            self.label_df = pd.read_csv(self.label_csv, index_col=[0])
            self.label_df['event_ts'] = pd.to_datetime(self.label_df.event_ts)
        else:
            #label
            if conn == None:
                conn = dh.get_connection(self.connection_credentials)
            with open('database/label.sql','r') as file:
                sql_query = file.read()
            sql_query = sql_query.replace(r'$P{rqstr_party_id}',str(self.rqstr_party_id))
            sql_query = sql_query.replace(r'$P{from_timestamp}','\''+self.label_from_timestamp+'\'')
            sql_query = sql_query.replace(r'$P{to_timestamp}','\''+self.to_timestamp+'\'')
            sql_query = sql_query.replace(r'$P{label_time_interval}','\''+self.label_time_interval+'\'')
            sql_query = sql_query.replace(r'$P{label_time_interval}','\''+self.label_time_interval+'\'')
            self.label_df = pd.read_sql(sql_query, conn,parse_dates={'event_ts':'%y-%m-%d %H:%M:%S'})

        #deal with inputs
        # check if saved csv file exists. If yes, read it instead of processing
        if (os.path.exists(self.input_csv)):
            self.input_df = pd.read_csv(self.input_csv, index_col=[0])
            self.input_df['event_ts'] = pd.to_datetime(self.input_df.event_ts)
        else:            
            #HACK: below is just, ugh. Please format the below per handler or something
            if conn == None:
                conn = dh.get_connection(self.connection_credentials)
            # get the input data for the given customer
            self.timestamp_df = pd.DataFrame(columns = ['event_ts','event_type'])
            self.df_dict = {}
            self.df_index_dict = {}
            self.input_df = pd.DataFrame()
            for event_type in self.event_list:
                if event_type == rc.EVENT_TYPE.date:
                    continue
                # FIXME: feed sql query locations instead of hard coding them
                with open('database/'+event_type.value+'.sql','r') as file:
                    sql_query = file.read()
                ccy_pair_list_ = str(self.ccy_pair_list)
                ccy_pair_list_ = ccy_pair_list_.replace("[","(")
                ccy_pair_list_ = ccy_pair_list_.replace("]",")")
                sql_query = sql_query.replace(r'$P{ccy_pair_list}',ccy_pair_list_)
                sql_query = sql_query.replace(r'$P{rqstr_party_id}',str(self.rqstr_party_id))
                sql_query = sql_query.replace(r'$P{from_timestamp}','\''+self.from_timestamp+'\'')
                sql_query = sql_query.replace(r'$P{to_timestamp}','\''+self.to_timestamp+'\'')
                sql_query = sql_query.replace(r'$P{cs_period_multiplier}','\''+self.cs_period_multiplier+'\'')
                sql_query = sql_query.replace(r'$P{cs_period_unit_cd}','\''+self.cs_period_unit_cd+'\'')
                df = pd.read_sql(sql_query, conn,parse_dates={'event_ts':'%y-%m-%d %H:%M:%S','valuedate':'%y-%m-%d %H:%M:%S'})

                temp_df = df['event_ts'].to_frame()
                temp_df.insert(1,'event_type',[event_type]*len(df),True)
                self.timestamp_df = self.timestamp_df.append(temp_df)
                self.df_dict[event_type] = df
                self.df_index_dict[event_type] = 0
            #Order the events in the timestamp_df
            self.timestamp_df = self.timestamp_df.sort_values(by=['event_ts'])
            #write the ordered events as inputs
            for index,row in self.timestamp_df.iterrows():
                self.event_handler(row['event_type'])

        try:
            conn.close()
        except:
            pass
        
        return [self.input_df,self.label_df]

    def event_handler(self,event_type):
        ir = {}
        row = self.df_dict[event_type].iloc[self.df_index_dict[event_type]]
        event_ts = row['event_ts']
        ir['event_ts'] = event_ts
        ir['event_type'] = event_type.value

        if event_type == rc.EVENT_TYPE.ccypos:
            self.ccy_pos_handler.handle_event(
                row['valuedate'].date(),
                row['currency'],
                row['currencyamt'])
        
        if rc.EVENT_TYPE.ccypos in self.event_list:
            data_dict = self.ccy_pos_handler.get_data(event_ts)
            for key in data_dict:
                ir[key] = data_dict[key]

        if event_type == rc.EVENT_TYPE.cs:
            self.cs_handler.handle_event(row['symbol'],
                            row['o'],
                            row['h'],
                            row['l'],
                            row['c'])

        if rc.EVENT_TYPE.cs in self.event_list:
            data_dict = self.cs_handler.get_data()
            for key in data_dict:
                #TODO: add the time interval of cs as a part of the name
                ir[key] = data_dict[key]

        if event_type == rc.EVENT_TYPE.login:
            self.login_event_handler.handle_event(row['isLogin'])
        
        if rc.EVENT_TYPE.login in self.event_list:
            data_dict= self.login_event_handler.send_data()
            for key in data_dict:
                ir[key] = data_dict[key]

        if event_type == rc.EVENT_TYPE.panel:
            #FIXME: this is empty in db, so it can be ignored
            pass

        if rc.EVENT_TYPE.panel in self.event_list:
            #FIXME: this is empty in db, so it can be ignored
            pass

        if event_type == rc.EVENT_TYPE.pos:
            self.pos_event_handler.handle_event(
                row['valuedate'],
                row['symbol'],
                row['currency1amt'],
                row['currency2amt']
            )

        if rc.EVENT_TYPE.pos in self.event_list:
            data_dict = self.pos_event_handler.send_data(event_ts)
            for key in data_dict:
                ir[key] = data_dict[key]


        if event_type == rc.EVENT_TYPE.transaction:
            self.transaction_event_handler.handle_event(
                event_ts,
                row['instrument_cd'],
                row['trade_state_cd'],
                row['rqstr_trade_action_cd'],
                row['trade_volumebase']
            )

        if rc.EVENT_TYPE.transaction in self.event_list:
            data_dict = self.transaction_event_handler.send_data(event_ts)
            for key in data_dict:
                ir[key] = data_dict[key]

        if rc.EVENT_TYPE.date in self.event_list:
            data_dict = self.transaction_event_handler.send_data(event_ts)
            for key in data_dict:
                ir[key] = data_dict[key]

        self.df_index_dict[event_type] += 1        
        
        #append to self.input_df
        self.input_df = self.input_df.append(ir,ignore_index=True)