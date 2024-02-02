from sklearn import linear_model
import provider as pv
import influx
import pandas as pd
import numpy as np

class Analyst:

    def __init__(self, deployment = "local"):
        self.provider = pv.Provider(deployment = deployment)
        self.influx = influx.InfluxDatabase(deployment = deployment)
    
    def impact_analysis(self, start = pd.Timestamp("2023-01-01T00:00"), stop = pd.Timestamp("2024-01-01T00:00"), currency = "USD", impact = "High"):
        """Build Dataframe for Impact Analysis"""

        raw_economic_calendar = self.influx.query_events(start = start, stop = stop, currency = currency, impact = impact)
        nice_economic_calendar = self.influx.preprocess_query_dataframe(raw_economic_calendar)

        currency_pair_map = {   "USD": "EURUSD",
                                "EUR": "EURUSD",
                                "GBP": "GBPUSD",
                                "NZD": "NZDUSD",
                                "CAD": "USDCAD",
                                "CHF": "USDCHF",
                                "JPY": "USDJPY"}
        
        pair = currency_pair_map[currency]

        impact_frame = nice_economic_calendar.sort_index(ascending=False)
        impact_frame["timestamp"] = impact_frame.index
        impact_frame["pair"] = pair
        impact_frame["deviation"] = (impact_frame["actual"] - impact_frame["estimate"]) / impact_frame["estimate"]
        impact_frame["price now open"] = impact_frame["timestamp"].apply(self.get_fx_price, args=(pair, "open",))
        impact_frame["price now close"] = impact_frame["timestamp"].apply(self.get_fx_price, args=(pair, "close",))
        impact_frame["price 5min"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=5)).apply(self.get_fx_price, args=(pair, "close",))
        impact_frame["price 10min"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=10)).apply(self.get_fx_price, args=(pair, "close",))
        impact_frame["price 30min"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=30)).apply(self.get_fx_price, args=(pair, "close",))
        
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

    def get_fx_price(self, datetime, pair = "EURUSD", price = "close"):
        """Get Foreign Exchange Price"""

        return self.provider.foreign_exchange_rate_minute_close(datetime, pair = pair, price = price)

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
        model = linear_model.LinearRegression()

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
    
    def economic_calendar(self, start, stop, currency = "USD", impact = "High"):
        """Get Economic Calendar"""
        raw_economic_calendar = self.influx.query_events(start = pd.Timestamp(start), stop = pd.Timestamp(stop), currency = currency, impact = impact)
        nice_economic_calendar = self.influx.preprocess_query_dataframe(raw_economic_calendar)
        pretty_economic_calendar = self.pretty_economic_calendar(nice_economic_calendar)
        return pretty_economic_calendar
    
    def pretty_economic_calendar(self, data_frame):
        """Pretty up Economic Calendar for Presentation"""
        data_frame.drop(columns=["currency", "impact", "source"], inplace=True)
        data_frame.columns = data_frame.columns.str.capitalize()
        return data_frame.loc[:,["Event", "Actual", "Estimate"]]