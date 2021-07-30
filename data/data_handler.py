#TODO LATER: enumerate event_type
#TODO LATER: somehow tell the algo that events happened X hours before predictions. Maybe num_days_since_last_activity?
#TODO LATER: self.ccy_pair_variables is too shaky. Have an individual tracker object for each event and/or ccy pair
#TODO LATER: data processing takes too long

import pandas as pd
import database.database_handler as dh
from data.input_row import InputRow as IR
from data.cs import CS
from data.ccypos import CcyPos
from data.pos import Pos
from datetime import datetime
import os


class CustomerDataHandler:
    #FIXME: tracking variables for event_types. Probably need to be in their own class for handling, tracking...
    #TODO LATER: ability to change ccy_pair_list based on query (watch out for input_row object, that will need to be changed as well!)
    def __init__(self, rqstr_party_id = 741,
                event_list = ['ccypos','cs','login','panel','pos','transaction'],
                ccy_pair_list = ['USDCAD','EURUSD','EURCAD','GBPUSD'],
                from_timestamp = '2020-01-01 00:00:00',
                to_timestamp = '2020-01-07 08:59:59',
                label_starting_time = '09:00:00',
                label_time_interval='24 hours',
                connection_credentials = 'database/credentials.json',
                input_csv = None,
                label_csv = None):
        
        self.rqstr_party_id = rqstr_party_id
        self.event_list = event_list
        self.ccy_pair_list = ccy_pair_list
        self.ccy_pair_variables = {}
        for ccy_pair in ccy_pair_list:
            self.ccy_pair_variables[ccy_pair] = {}
        self.from_timestamp = from_timestamp
        self.to_timestamp = to_timestamp
        self.label_starting_time = label_starting_time
        self.label_time_interval = label_time_interval
        self.connection_credentials = connection_credentials
        self.input_csv = input_csv
        self.label_csv = label_csv

        self.numberOfUsers = 0
        self.previous_event_ts = None
        self.next_label_ts = None
        self.next_label_index = 0
        self.previous_row = IR()
        self.ccy_list = set()
        for ccy_pair in ccy_pair_list:
            self.ccy_list.add(ccy_pair[0:3])
            self.ccy_list.add(ccy_pair[3:6])
        self.label_from_timestamp = from_timestamp[:-8] + self.label_starting_time


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
            self.label_df = pd.read_sql(sql_query, conn,parse_dates={'event_ts':'%y-%m-%d %H:%M:%S'})
            self.next_label_ts = self.label_df.iloc[0]['event_ts']

        # check if saved csv file exists. If yes, read it instead of processing
        if (os.path.exists(self.input_csv)):
            self.input_df = pd.read_csv(self.input_csv, index_col=[0])
            self.input_df['event_ts'] = pd.to_datetime(self.input_df.event_ts)
        else:            
            if conn == None:
                conn = dh.get_connection(self.connection_credentials)
            # get the input data for the given customer
            self.timestamp_df = pd.DataFrame(columns = ['event_ts','event_type'])
            self.df_dict = {}
            self.df_index_dict = {}
            self.input_df = pd.DataFrame()
            for event_type in self.event_list:
                # FIXME: feed sql query locations instead of hard coding them
                with open('database/'+event_type+'.sql','r') as file:
                    sql_query = file.read()
                ccy_pair_list_ = str(self.ccy_pair_list)
                ccy_pair_list_ = ccy_pair_list_.replace("[","(")
                ccy_pair_list_ = ccy_pair_list_.replace("]",")")
                sql_query = sql_query.replace(r'$P{ccy_pair_list}',ccy_pair_list_)
                sql_query = sql_query.replace(r'$P{rqstr_party_id}',str(self.rqstr_party_id))
                sql_query = sql_query.replace(r'$P{from_timestamp}','\''+self.from_timestamp+'\'')
                sql_query = sql_query.replace(r'$P{to_timestamp}','\''+self.to_timestamp+'\'')
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
        ir = IR()
        ir = ir.to_dict()
        row = self.df_dict[event_type].iloc[self.df_index_dict[event_type]]
        event_ts = row['event_ts']
        ir['event_ts'] = event_ts
        ir['event_type'] = event_type

        #update the next event label for candlesticks etc.
        if event_ts>=self.next_label_ts:
            try:
                self.next_label_ts = self.label_df.iloc[self.next_label_index]['event_ts']
                self.next_label_index +=1
            except:
                pass
        #update input row according to the event 
        if event_type == 'ccypos':
            valueDate = row['valuedate']
            currency = row['currency']
            currencyAmt = row['currencyamt']
            for ccy_pair in self.ccy_pair_list:
                if currency in ccy_pair:
                    self.ccy_pair_variables[ccy_pair]['exposure'+str(valueDate.date())+currency]= CcyPos(currency,valueDate,currencyAmt)
        
        for ccy_pair in self.ccy_pair_list:
            ccy_list = [ccy_pair[0:3],ccy_pair[3:6]]
            for ccy in ccy_list:
                try:
                    ccypos = self.ccy_pair_variables[ccy_pair]['exposure'+str(event_ts.date())+ccy] 
                    ir[ccy_pair+ccy+'exposure'] = ccypos.currencyAmt
                except:
                    pass 


        if event_type == 'cs':
            ir['CS'] = 1
            symbol = row['symbol']
            ir[symbol] = 1
            o=row['o']
            h=row['h']
            l=row['l']
            c=row['c']

            #this is the first CS
            if str('cs') not in self.ccy_pair_variables[symbol]:
                self.ccy_pair_variables[symbol]['cs'] = CS(symbol,self.next_label_ts,o,h,l,c)

            #update CS - if it needs to be a new CS, updated = False
            updated = self.ccy_pair_variables[symbol]['cs'].update(event_ts,o,h,l,c)
            #this is a new CS
            if not updated :
                self.ccy_pair_variables[symbol]['cs'] = CS(symbol,self.next_label_ts,o,h,l,c)

        for symbol in self.ccy_pair_list:
            if 'cs' in self.ccy_pair_variables[symbol]:
                cs = self.ccy_pair_variables[symbol]['cs']
                if cs.period_end_ts >= event_ts:
                    ir[symbol+'dailyCSOPen'] = self.ccy_pair_variables[symbol]['cs'].o
                    ir[symbol+'dailyCSHigh'] = self.ccy_pair_variables[symbol]['cs'].h
                    ir[symbol+'dailyCSLow'] = self.ccy_pair_variables[symbol]['cs'].l
                    ir[symbol+'dailyCSCLOSE'] = self.ccy_pair_variables[symbol]['cs'].c

        if event_type == 'login':
            if row['islogin']:
                self.numberOfUsers+=1
                ir['LOGIN'] = 1
            else:
                self.numberOfUsers-=1
                ir['LOGOUT'] = 1 
        
        # numberOfUsers
        ir['numberOfUsers'] = self.numberOfUsers

        if event_type == 'panel':
            #FIXME: this is empty in db, so it can be ignored
            pass
        
        if event_type == 'pos':
            symbol = row['symbol']
            valueDate = row['valuedate']
            currency1Amt = row['currency1amt']
            currency2Amt = row['currency2amt']
            self.ccy_pair_variables[symbol]['pos'+str(valueDate.date())]= Pos(symbol,valueDate,currency1Amt,currency2Amt)
        
        for ccy_pair in self.ccy_pair_list:
            try:
                pos = self.ccy_pair_variables[ccy_pair]['pos'+str(event_ts.date())]
                ir[ccy_pair+'basePos'] = pos.currency1Amt
                ir[ccy_pair+'termPos'] = pos.currency2Amt
                ir[ccy_pair+'posRate'] = pos.currency1Amt/pos.currency2Amt
            except:
                pass

        
        if event_type == 'transaction':
            instrument_cd = row['instrument_cd']
            self.ccy_pair_variables[instrument_cd]['previous_event_ts'] = event_ts

            ir[row['trade_state_cd']]=1
            ir[instrument_cd] = 1
            ir[row['rqstr_trade_action_cd']] = 1
            ir['size'] = row['trade_volumebase']
            

        # TODO LATER: clear ccy_pair_dicts when needed EFFECTIVELY
        # check if the day changed since the last ts
        # if (datetime.strptime(self.previous_event_ts,'%Y-%m-%d %H:%M:%S')).date() < (datetime.strptime(event_ts,'%Y-%m-%d %H:%M:%S')).date():
        #     for ccy_pair in self.ccy_pair_list:
        #         # exposure
        #         ccy_list = [ccy_pair[0:3],ccy_pair[3:6]]
        #         for ccy in ccy_list:
        #             if 'exposure' in self.ccy_pair_variables[ccy_pair]:
        #                 test[8:18]

        #time delta shenanigans
        if self.previous_event_ts == None:
            ir['timeDelta'] = 0
        else:
            ir['timeDelta'] = (event_ts - self.previous_event_ts).total_seconds()
        self.previous_event_ts = event_ts

        #ccy_pair+timeDelta vars that have not been updated
        for ccy_pair in self.ccy_pair_list:
            previous_event_ts = None
            if 'previous_event_ts' in self.ccy_pair_variables[ccy_pair]:
                previous_event_ts = self.ccy_pair_variables[ccy_pair]['previous_event_ts']
            else:
                previous_event_ts = event_ts
            ir[ccy_pair+'timeDelta'] = (event_ts - previous_event_ts).total_seconds()

        self.df_index_dict[event_type] += 1
        self.previous_row = ir
        
        
        #append to self.input_df
        self.input_df = self.input_df.append(ir,ignore_index=True)