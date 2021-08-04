from datetime import datetime,date

class CcyPosEventHandler:
    def __init__(self, ccy_list:list,_num_value_dates_before_part_value_date_clean:int = 30):
        self.ccy_list = ccy_list
        #NOTE: in format of data_dict[valueDate][ccy]
        self.data_dict = {}
        self._num_value_dates_before_part_value_date_clean = _num_value_dates_before_part_value_date_clean

    def handle_event(self, valuedate:date, ccy:str, currencyAmt:float):
        if valuedate not in self.data_dict:
            self.data_dict[valuedate] = {}
        #NOTE: Not using <ccy_pair><ccy> format, just using <ccy> format 
        self.data_dict[valuedate][ccy] = currencyAmt
        
    #this can be called to get pos details for the current event_ts
    def get_data(self,event_ts:datetime):
        event_date = event_ts.date()
        # delete outdated data if we hit the threshold # of value dates
        if len(self.data_dict) > self._num_value_dates_before_part_value_date_clean:
            self._delete_past_value_dates(event_date)
        result = {}
        # we have entries for this value date
        if event_date in self.data_dict:
            for ccy in self.ccy_list:
                if ccy in self.data_dict[event_date]:
                    result[ccy + 'Exposure'] = self.data_dict[event_date][ccy]
                else:
                    result[ccy + 'Exposure'] = 0
        else:
            for ccy in self.ccy_list:
                result[ccy + 'Exposure'] = 0

        return result
    
    #delete value dates that have expired
    def _delete_past_value_dates(self,event_date:date):
        value_dates_to_delete = []
        for value_date in self.data_dict:
            if value_date < event_date:
                value_dates_to_delete.append(value_date)
        for value_date in value_dates_to_delete:
            self.data_dict.pop(value_date)
