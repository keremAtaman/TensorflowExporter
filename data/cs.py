#TODO LATER: add datetime.timedelta and revamp period_end_ts

class CS:
    def __init__(self,symbol,period_end_ts,
                o,h,l,c):
        self.symbol = symbol
        self.period_end_ts = period_end_ts
        self.o=o
        self.h=h
        self.l=l
        self.c=c
    
    def update(self,timestamp,o,h,l,c):
        if timestamp>= self.period_end_ts:
            return False
        
        if self.h<h:
            self.h=h
        if self.l>l:
            self.l=l
        self.c=c