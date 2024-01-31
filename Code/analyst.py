from sklearn.linear_model import LinearRegression
import provider as pv
import influx
import pandas as pd
import numpy as np

class Analyst:

    def __init__(self, deployment = "local"):
        self.provider = pv.Provider()
        self.influx = influx.InfluxDatabase(deployment = "streamlit")

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
    
    def new_impact_analysis(self, start = pd.Timestamp("2023-01-01T00:00"), stop = pd.Timestamp("2024-01-01T00:00")):
        """Build Dataframe for Impact Analysis"""

        raw_economic_calendar = self.influx.query_events(start = start, stop = stop)
        nice_economic_calendar = self.influx.preprocess_query_dataframe(raw_economic_calendar)

        impact_frame = nice_economic_calendar.sort_index(ascending=False)
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
        
        impact_frame.drop(columns=["timestamp"], inplace=True)

        return impact_frame

    def postprocess_impact_frame(self, impact_frame):
        """Clean Impact Frame Infinite Values and NaN Values"""

        impact_frame.replace([np.inf, - np.inf], np.nan, inplace = True)
        impact_frame.dropna(inplace = True)

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

    def regression_analysis(self, model, x_series, y_series):
        """Get Coefficient of Determination, Intercept and Slope of Regression Analysis"""

        x_series = x_series.replace([np.inf, - np.inf], np.nan, inplace = False)
        y_series = y_series.replace([np.inf, - np.inf], np.nan, inplace = False)
        x_series.dropna(inplace = True)
        y_series.dropna(inplace = True)

        x = x_series.to_numpy()
        y = y_series.to_numpy()
        
        x = x.reshape(-1, 1)
        y = y.reshape(-1, 1)

        model.fit(x, y)

        cod = model.score(x, y)
        intercept = model.intercept_
        slope = model.coef_

        return cod, intercept[0], slope[0][0]
    
    def make_regression_frame(self, impact_frame):
        """Make Regression Frame from Impact Frame"""

        unique_events = impact_frame["event"].unique()
        groups = impact_frame.groupby("event")
        model = LinearRegression()

        records = []
        names = []

        for event in unique_events:
            group = groups.get_group(event)
            count = group.shape[0]
            cod_original_impact = self.regression_analysis(model, group["deviation"], group["original impact"])[0]
            cod_first_impact = self.regression_analysis(model, group["deviation"], group["first impact"])[0]
            cod_second_impact = self.regression_analysis(model, group["deviation"], group["second impact"])[0]
            cod_third_impact = self.regression_analysis(model, group["deviation"], group["third impact"])[0]

            record = [count, cod_original_impact, cod_first_impact, cod_second_impact, cod_third_impact]
            records.append(record)
            names.append(event)

        frame = pd.DataFrame(data = records, index=names, columns=["Count", "CoD Original Impact", "CoD First Impact", "CoD Second Impact", "CoD Third Impact"])

        return frame