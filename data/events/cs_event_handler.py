class CsEventHandler:
    def __init__(self,
                ccy_pair_list,
                cs_period_multiplier,
                cs_period_unit_cd):
        self.ccy_pair_list = ccy_pair_list
        #NOTE: in format of data_dict[ccy_pair][<o,h,l,c>]
        self.data_dict = {}
        for ccy_pair in ccy_pair_list:
            self.data_dict[ccy_pair] = {}
            for item_ in ['o','h','l','c']:
                self.data_dict[ccy_pair][item_] = 0
        
        self.cs_period_multiplier = cs_period_multiplier
        self.cs_period_unit_cd = cs_period_unit_cd

    def handle_event(self,ccy_pair,o,h,l,c):
        self.data_dict[ccy_pair]['o'] = o
        self.data_dict[ccy_pair]['h'] = h
        self.data_dict[ccy_pair]['l'] = l
        self.data_dict[ccy_pair]['c'] = c
    
    def get_data(self)->dict:
        result = {}
        for ccy_pair in self.ccy_pair_list:
            result[ccy_pair+self.cs_period_multiplier+self.cs_period_unit_cd+'Open'] = self.data_dict[ccy_pair]['o']
            result[ccy_pair+self.cs_period_multiplier+self.cs_period_unit_cd+'High'] = self.data_dict[ccy_pair]['h']
            result[ccy_pair+self.cs_period_multiplier+self.cs_period_unit_cd+'Low'] = self.data_dict[ccy_pair]['l']
            result[ccy_pair+self.cs_period_multiplier+self.cs_period_unit_cd+'Close'] = self.data_dict[ccy_pair]['c']
        return result