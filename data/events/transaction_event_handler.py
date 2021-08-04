from datetime import datetime
from typing import List

class TransactionEventHandler:
    def __init__(self,
                trade_state_cd_list:List[str],
                rqstr_trade_action_cd_list:List[str],
                ccy_pair_list:List[str]):
        self.previous_event_ts = None
        self.trade_state_cd_list = trade_state_cd_list
        self.rqstr_trade_action_cd_list = rqstr_trade_action_cd_list
        self.ccy_pair_list = ccy_pair_list
        self.data_dict = {}
        self.previous_event_dict = {}
        self.current_event_was_transaction:bool = False

    def handle_event(self, 
                    event_ts:datetime,
                    ccy_pair:str, 
                    trade_state_cd:str,
                    rqstr_trade_action_cd:str,
                    size:float):
        for trade_state_cd_ in self.trade_state_cd_list:
            self.data_dict[trade_state_cd_] = 0
        for ccy_pair_ in self.ccy_pair_list:
            self.data_dict[ccy_pair_ + 'transaction'] = 0
        for action in self.rqstr_trade_action_cd_list:
            self.data_dict[action] = 0

        self.data_dict[ccy_pair + 'transaction'] = 1
        self.data_dict[trade_state_cd] = 1
        self.data_dict[rqstr_trade_action_cd] = 1
        self.data_dict['size'] = size
        if self.previous_event_ts == None:
            self.data_dict['timeDelta'] = 0
        else:
            self.data_dict['timeDelta'] = (event_ts - self.previous_event_ts).total_seconds()

        for ccy_pair_ in self.ccy_pair_list:
            if ccy_pair_ in self.previous_event_dict:
                self.data_dict[ccy_pair_+'timeDelta'] = (event_ts - self.previous_event_dict[ccy_pair_]).total_seconds()
            else:
                self.data_dict[ccy_pair_+'timeDelta'] = 0
        
        self.previous_event_ts = event_ts
        self.previous_event_dict[ccy_pair] = event_ts
        self.current_event_was_transaction = True
        
    def send_data(self,event_ts):
        result = {}
        #FIXME: this one is buggy, what happens when this is called before entries OR when there are no recent entries
        if self.current_event_was_transaction:
            self.current_event_was_transaction = False
            result = self.data_dict
        else:
            # TODO: replicate the logic below, as majority is being used in handle_data as well
            for trade_state_cd_ in self.trade_state_cd_list:
                result[trade_state_cd_] = 0
            for ccy_pair_ in self.ccy_pair_list:
                result[ccy_pair_ + 'transaction'] = 0
            for action in self.rqstr_trade_action_cd_list:
                result[action] = 0
            if self.previous_event_ts == None:
                result['timeDelta'] = 0
            else:
                result['timeDelta'] = (event_ts - self.previous_event_ts).total_seconds()
            for ccy_pair_ in self.ccy_pair_list:
                if ccy_pair_ in self.previous_event_dict:
                    result[ccy_pair_+'timeDelta'] = (event_ts - self.previous_event_dict[ccy_pair_]).total_seconds()
                else:
                    result[ccy_pair_+'timeDelta'] = 0
            result['size'] = 0

        return result