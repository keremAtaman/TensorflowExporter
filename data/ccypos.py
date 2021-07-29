class CcyPos:
    def __init__(self,currency,valueDate,currencyAmt):
        self.currency = currency
        self.valueDate = valueDate
        self.currencyAmt = currencyAmt

    def update(self,valueDate,currencyAmt):
        if valueDate != self.valueDate:
            return False

        self.currencyAmt=currencyAmt