from datetime import datetime,date,timedelta
from pandas.tseries.offsets import BMonthEnd

class DateEventHandler:
    def send_data(self, event_ts:datetime):
        event_date:date = event_ts.date()
        # TODO: distance to first/last days
        day_of_week = event_date.weekday()
        day_of_month = event_date.day()
        month_of_year = event_date.month
        monday_of_week = event_date - timedelta(days = day_of_week)
        friday_of_week = event_date + timedelta(days = (4 - day_of_week))
        first_day_of_month = event_date.replace(day=1)
        last_day_of_month = self.get_last_day_of_month(event_date)
        first_business_day_of_month = self.get_first_business_day_of_month(event_date)
        last_business_day_of_month = self.get_last_business_day_of_month(event_date)

        return {
            'day_of_week': day_of_week,
            'day_of_month': day_of_month,
            'month_of_year':month_of_year
        }

    def get_first_business_day_of_month(self,event_date:date):
        first_day = self.get_first_day_of_month(event_date)
        if first_day.weekday() < 5:
            return first_day
        else:
            return first_day + timedelta(days = (first_day.weekday()%4))
    
    def get_last_day_of_month(self,event_date:date):
        offset = BMonthEnd()
        # last day of current month
        return offset.rollforward(event_date)

    def get_last_business_day_of_month(self,event_date:date):
        last_day_of_month = self.get_last_day_of_month(event_date)
        subtractor = last_day_of_month.weekday() - 4
        if subtractor > 0:
            return last_day_of_month - timedelta(days = subtractor)
        else:
            return last_day_of_month