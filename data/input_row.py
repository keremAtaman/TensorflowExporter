#TODO LATER: we currently convert this to a dict then work with it. see if there is a better way
#TODO LATER: allow customizing of features, ccy pairs etc. Maybe drop this and just use a dictionary...

class InputRow:
    def __init__(self):
        self.event_ts = None
        self.event_type = None

        self.LOGIN = 0
        self.LOGOUT = 0
        self.PANEL = 0
        self.RFQ_CT_CANCEL = 0
        self.RFQ_EXPIRED = 0
        self.RFQ_REJECT = 0
        self.RFQ_TIMEOUT = 0
        self.RFQ_SUBMITTED = 0
        self.TRADE_DONE = 0
        self.TRADE_REJECT = 0
        self.RFS_PENDING = 0
        self.RFS_CANCEL = 0
        self.CS = 0
        self.USDCAD = 0
        self.EURCAD = 0
        self.GBPUSD = 0
        self.EURUSD = 0
        self.B = 0
        self.S = 0
        self.BS = 0
        self.size = 0
        self.timeDelta = 0
        self.numberOfUsers = 0
        #FIXME: credit variables not included as they are not in data atm
        #FIXME: <ccy pair> <volatility> variables not included as they are not in data atm
        #FIXME: <ccy pair> <TRANS_STATE_CD> variables not included as they can be found from other cols
        #FIXME: <ccy pair> <TRADE_ACTION_CD (e.g. Buy)> variables not included as they can be found from other cols
        #FIXME: <ccy pair> <# of RFSes> variables not included as they are not in data atm
        #FIXME: <ccy pair> event_size variables not included as they can be found from other cols
        self.USDCADbasePos = 0
        self.USDCADtermPos = 0
        self.USDCADUSDexposure = 0
        self.USDCADCADexposure = 0
        self.USDCADposRate = 0
        self.USDCADdailyCSOPen = 0
        self.USDCADdailyCSHigh = 0
        self.USDCADdailyCSLow = 0
        self.USDCADdailyCSCLOSE = 0
        self.USDCADtimeDelta = 0
        self.EURCADbasePos = 0
        self.EURCADtermPos = 0
        self.EURCADEURexposure = 0
        self.EURCADCADexposure = 0
        self.EURCADposRate = 0
        self.EURCADdailyCSOPen = 0
        self.EURCADdailyCSHigh = 0
        self.EURCADdailyCSLow = 0
        self.EURCADdailyCSCLOSE = 0
        self.EURCADtimeDelta = 0
        self.GBPUSDbasePos = 0
        self.GBPUSDtermPos = 0
        self.GBPUSDGBPexposure = 0
        self.GBPUSDUSDexposure = 0
        self.GBPUSDposRate = 0
        self.GBPUSDdailyCSOPen = 0
        self.GBPUSDdailyCSHigh = 0
        self.GBPUSDdailyCSLow = 0
        self.GBPUSDdailyCSCLOSE = 0
        self.GBPUSDtimeDelta = 0
        self.EURUSDbasePos = 0
        self.EURUSDtermPos = 0
        self.EURUSDEURexposure = 0
        self.EURUSDUSDexposure = 0
        self.EURUSDposRate = 0
        self.EURUSDdailyCSOPen = 0
        self.EURUSDdailyCSHigh = 0
        self.EURUSDdailyCSLow = 0
        self.EURUSDdailyCSCLOSE = 0
        self.EURUSDtimeDelta = 0

    def to_dict(self):
        return vars(self)

    def to_input_dict(self)->dict:
        """Returns a dictionary without the non-numerical class variables
            for easy data processing
        Returns:
            dict: the dictionary without non-numerical class variables
        """
        result = self.to_dict
        result.pop("event_ts")
        result.pop("event_type")
        return result
