class CurrencyPrediction():
    def __init__(self,direction,volume,last_3_months_avg):
        self.direction = direction
        self.volume = volume
        self.last_3_months_avg = last_3_months_avg

class PredictionInstance():
    def __init__(self,customer,ccy_pair,product_type,currency_1_prediction:CurrencyPrediction,currency_2_prediction:CurrencyPrediction):
        self.customer = customer
        self.ccy_pair = ccy_pair
        self.product_type = product_type
        self.currency_1_prediction = currency_1_prediction
        self.currency_2_prediction = currency_2_prediction