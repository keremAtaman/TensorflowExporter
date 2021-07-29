class Pos:
    def __init__(self,symbol,valueDate,currency1Amt,currency2Amt) -> None:
        self.symbol = symbol
        self.valueDate = valueDate
        self.currency1Amt = currency1Amt
        self.currency2Amt = currency2Amt
    
    
    def update(self,valueDate,currency1Amt,currency2Amt):
        if valueDate != self.valueDate:
            return False

        self.currency1Amt=currency1Amt
        self.currency2Amt=currency2Amt