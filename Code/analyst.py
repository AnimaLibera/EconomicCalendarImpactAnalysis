import provider as pv
import influx
import pandas as pd

class Analyst:

    def __init__(self):
        self.provider = pv.Provider()
        self.influx = influx.InfluxDatabase()
        self.nice_economic_calendar = self.influx.preprocess_query_dataframe(self.influx.query_events(start = pd.Timestamp("2023-01-01T00:00"), stop = pd.Timestamp("2024-01-01T00:00")))
        #self.raw_economic_calendar = self.provider.economic_calendar(start_date, end_date)
        #self.raw_events = self.extract_events()
        #self.clean_high_impact_events = self.clean_events(self.extract_high_impact_events())
        #self.raw_countrys = self.extract_countrys()
        #self.unique_countrys = set(self.raw_countrys)
        #self.fx_prices = self.provider.foreign_exchange_rates(start_date, end_date)

    def extract_events(self):
        """Extract Economic Calendar Events"""
        events = []
        for element in self.raw_economic_calendar:
            events.append(element["event"])
        return events
    
    def extract_high_impact_events(self):
        """Extract High Impact Events"""
        events = []
        for element in self.raw_economic_calendar:
            if element["impact"] == "High":
                events.append(element["event"])
        return events

    def clean_events(self, raw_events):
        """Clean Economic Calendar Events"""
        events = []
        for event in raw_events:
            events.append(self.clean_event(event))
        return set(events)

    def clean_event(self, event):
        """Clean Event"""
        for word in event.split():
            if self.is_parentess_word(word):
                event = event.replace(word, "").strip()
        return event
    
    def is_parentess_word(self, word):
        """Check if word is parenthesis word"""
        if word.startswith("(") and word.endswith(")"):
            return True
        else:
            return False
    
    def extract_countrys(self):
        """Extract Countries"""
        countrys = []
        for element in self.raw_economic_calendar:
            countrys.append(element["country"])
        return countrys
    
    def new_impact_analysis(self):
        """Build Dataframe for Impact Analysis"""

        impact_frame = self.nice_economic_calendar.sort_index(ascending=False)
        impact_frame["timestamp"] = impact_frame.index
        impact_frame["deviation"] = (impact_frame["actual"] - impact_frame["estimate"]) / impact_frame["estimate"]
        impact_frame["price now open"] = impact_frame["timestamp"].apply(self.get_fx_price, args=("open",))
        impact_frame["price now close"] = impact_frame["timestamp"].apply(self.get_fx_price, args=("close",))
        impact_frame["price 5min"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=5)).apply(self.get_fx_price, args=("close",))
        impact_frame["price 10min"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=10)).apply(self.get_fx_price, args=("close",))
        impact_frame["price 30min"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=30)).apply(self.get_fx_price, args=("close",))
        
        ###Calculate Impact in Basispoints###
        impact_frame["original impact"] = (impact_frame["price now close"] - impact_frame["price now open"]) / impact_frame["price now open"] * 10000
        impact_frame["first impact"] = (impact_frame["price 5min"] - impact_frame["price now close"]) / impact_frame["price now close"] * 10000
        impact_frame["second impact"] = (impact_frame["price 10min"] - impact_frame["price now close"]) / impact_frame["price now close"] * 10000
        impact_frame["third impact"] = (impact_frame["price 30min"] - impact_frame["price now close"]) / impact_frame["price now close"] * 10000

        return impact_frame

    def impact_analysis(self, country = "US", pair = "EURUSD"):
        """Build Dataframe for Impact Analysis"""

        dates = []
        records = []

        #print(self.fx_prices)

        for element in self.raw_economic_calendar:
            if element["impact"] == "High" and element["country"] == country:
                datetime = pd.Timestamp(element["date"]).tz_localize(tz="Etc/GMT")
                event = self.clean_event(element["event"])
                expectation = element["estimate"]
                actual = element["actual"]
                deviation = self.calculate_deviation(expectation, actual)
                price_now_open = self.get_fx_price(datetime, "open")
                price_now = self.get_fx_price(datetime) #Close
                price_1min = self.get_fx_price(datetime + pd.Timedelta(minutes=1))
                price_5min = self.get_fx_price(datetime + pd.Timedelta(minutes=5))
                price_10min = self.get_fx_price(datetime + pd.Timedelta(minutes=10))
                price_30min = self.get_fx_price(datetime + pd.Timedelta(minutes=30))
                original_impact = self.calculate_impact(price_now_open, price_now)
                first_impact = self.calculate_impact(price_now, price_5min)
                second_impact = self.calculate_impact(price_now, price_10min)
                third_impact = self.calculate_impact(price_now, price_30min)

                record = [event, expectation, actual, deviation, price_now_open, price_now, price_5min, price_10min, price_30min, original_impact, first_impact, second_impact, third_impact]
                dates.append(datetime)
                records.append(record)
        
        frame = pd.DataFrame(data = records, index=dates, columns=["Event", "Expectation", "Actual", "Deviation", "Price Now Open", "Price Now Close", "Price 5Min", "Price 10Min", "Price 30Min", "Original Impact", "First Impact", "Second Impact", "Third Impact"])

        return frame
    
    def calculate_deviation(self, expectation, actual):
        """Calculate Deviation"""
        if actual == None or expectation == None:
            return None
        elif expectation == 0:
            return expectation
        return (actual - expectation) / expectation
    
    #def get_fx_price(self, datetime):
    #    """Get Foreign Exchange Price"""
    #
    #    if datetime in self.fx_prices.index:
    #        return self.fx_prices[datetime]
    #    else:
    #        return None
    
    def get_fx_price(self, datetime, price = "close"):
        """Get Foreign Exchange Price"""

        return self.provider.foreign_exchange_rate_minute_close(datetime, pair = "EURUSD", price = price)
    

    def calculate_impact(self, old_price, new_price):
        """Calculate Impact in Basispoints"""
        if old_price == None or new_price == None:
            return None
        elif old_price == 0:
            return old_price
        return (new_price - old_price) / old_price * 10000
    

if __name__ == "__main__":

    start_date = "2024-01-01"
    end_date = "2024-01-25"
    analyst = Analyst(start_date, end_date)
    frame = analyst.new_impact_analysis()
    print(frame)
    frame.to_html("../Report/ImpactAnalysis.html")
    #group_frame = frame.groupby("event")["first impact"].count()
    #print(group_frame)
    grouped = frame.groupby("event")
    print(grouped.get_group("PPI MoM"))