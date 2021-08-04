from datetime import date
from typing import List

class PosEventHandler:
    def __init__(self,ccy_pair_list:List[str],_num_value_dates_before_part_value_date_clean:int = 30):
        self.ccy_pair_list = ccy_pair_list
        #NOTE: in format of data_dict[valueDate][ccy_pair][<ccy1Amt,ccy2Amt>]
        self.data_dict = {}
        self._num_value_dates_before_part_value_date_clean = _num_value_dates_before_part_value_date_clean
    def handle_event(self,valuedate:date,ccy_pair:str,currency1Amt:float,currency2Amt:float):
        valuedate = valuedate.date()
        if valuedate not in self.data_dict:
            self.data_dict[valuedate] = {}
        if ccy_pair not in self.data_dict[valuedate]:
            self.data_dict[valuedate][ccy_pair] = {}
        self.data_dict[valuedate][ccy_pair]['currency1Amt'] = currency1Amt
        self.data_dict[valuedate][ccy_pair]['currency2Amt'] = currency2Amt
        pass
    def send_data(self,event_ts):
        event_date = event_ts.date()
        if len(self.data_dict) > self._num_value_dates_before_part_value_date_clean:
            self._delete_past_value_dates(event_date)
        result = {}
        if event_date in self.data_dict:
            for ccy_pair in self.ccy_pair_list:
                if ccy_pair in self.data_dict[event_date]:
                    result[ccy_pair + 'basePos'] = self.data_dict[event_date][ccy_pair]['currency1Amt']
                    result[ccy_pair + 'termPos'] = self.data_dict[event_date][ccy_pair]['currency2Amt']
                else:
                    result[ccy_pair + 'basePos'] = 0
                    result[ccy_pair + 'termPos'] = 0
        else:
            for ccy_pair in self.ccy_pair_list:
                result[ccy_pair + 'basePos'] = 0
                result[ccy_pair + 'termPos'] = 0

        return result
    
    #delete value dates that have expired
    def _delete_past_value_dates(self,event_date:date):
        value_dates_to_delete = []
        for value_date in self.data_dict:
            if value_date < event_date:
                value_dates_to_delete.append(value_date)
        for value_date in value_dates_to_delete:
            self.data_dict.pop(value_date)