from sklearn import linear_model
import provider as pv
import streamlit as st
import influx
import pandas as pd
import numpy as np

class Analyst:

    def __init__(self, deployment = "local", source="MetaTrader5"):
        self.provider = pv.Provider(deployment = deployment)
        self.influx = influx.InfluxDatabase(deployment = deployment)
        self.price_data_source = source
    
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
                                "JPY": "USDJPY",
                                "AUD": "AUDUSD"}
        
        pair = currency_pair_map[currency]

        impact_frame = nice_economic_calendar.sort_index(ascending=False)
        impact_frame["timestamp"] = impact_frame.index
        impact_frame["pair"] = pair
        impact_frame["deviation"] = (impact_frame["actual"] - impact_frame["estimate"]) / impact_frame["estimate"]
        #impact_frame["price now open"] = (impact_frame["timestamp"] - pd.Timedelta(minutes=1)).apply(self.get_fx_price, args=(pair, "close", self.price_data_source))
        impact_frame["price now open"] = impact_frame["timestamp"].apply(self.get_fx_price, args=(pair, "open", self.price_data_source))
        impact_frame["price now close"] = impact_frame["timestamp"].apply(self.get_fx_price, args=(pair, "close", self.price_data_source))
        impact_frame["price 5min"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=5)).apply(self.get_fx_price, args=(pair, "close", self.price_data_source))
        impact_frame["price 10min"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=10)).apply(self.get_fx_price, args=(pair, "close", self.price_data_source))
        impact_frame["price 30min"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=30)).apply(self.get_fx_price, args=(pair, "close", self.price_data_source))
        impact_frame["price 1h"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=60)).apply(self.get_fx_price, args=(pair, "close", self.price_data_source))
        impact_frame["price 2h"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=120)).apply(self.get_fx_price, args=(pair, "close", self.price_data_source))
        impact_frame["price 3h"] = (impact_frame["timestamp"] + pd.Timedelta(minutes=180)).apply(self.get_fx_price, args=(pair, "close", self.price_data_source))

        ###Calculate Impact in Basispoints###
        impact_frame["original impact"] = (impact_frame["price now close"] - impact_frame["price now open"]) / impact_frame["price now open"] * 10000
        impact_frame["first impact"] = (impact_frame["price 5min"] - impact_frame["price now close"]) / impact_frame["price now close"] * 10000
        impact_frame["second impact"] = (impact_frame["price 10min"] - impact_frame["price now close"]) / impact_frame["price now close"] * 10000
        impact_frame["third impact"] = (impact_frame["price 30min"] - impact_frame["price now close"]) / impact_frame["price now close"] * 10000
        impact_frame["one hour impact"] = (impact_frame["price 1h"] - impact_frame["price now close"]) / impact_frame["price now close"] * 10000
        impact_frame["tow hour impact"] = (impact_frame["price 2h"] - impact_frame["price now close"]) / impact_frame["price now close"] * 10000
        impact_frame["three hour impact"] = (impact_frame["price 3h"] - impact_frame["price now close"]) / impact_frame["price now close"] * 10000

        impact_frame.drop(columns=["timestamp"], inplace=True)

        return impact_frame

    def postprocess_impact_frame(self, impact_frame):
        """Clean Impact Frame Infinite Values and NaN Values"""

        impact_frame.replace([np.inf, - np.inf], np.nan, inplace = True)
        impact_frame.dropna(inplace = True)

        return impact_frame
    
    def pretty_impact_analsysis(self, data_frame):
        """Pretty up Impact Analysis for Presentation"""

        data_frame.drop(columns=["currency", "impact", "source", "pair"], inplace=True)
        data_frame.columns = data_frame.columns.str.capitalize()
        well_orderd_columns = data_frame.columns.tolist()
        well_orderd_columns.remove("Event")
        well_orderd_columns.insert(0, "Event")

        return data_frame.loc[:,well_orderd_columns]

    def get_fx_price(self, datetime, pair = "EURUSD", price = "close", source="MetaTrader5"):
        """Get Foreign Exchange Price"""

        print(f"Get FX Price: Timestamp {datetime}, Pair {pair}, Price {price}, Source {source}")
        return self.provider.foreign_exchange_rate_minute(datetime, pair = pair, price = price, source=source)

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
            cod_one_hour_impact = self.regression_analysis(model, group["deviation"], group["one hour impact"])[0]
            cod_tow_hour_impact = self.regression_analysis(model, group["deviation"], group["tow hour impact"])[0]
            cod_three_hour_impact = self.regression_analysis(model, group["deviation"], group["three hour impact"])[0]

            record = [count, cod_original_impact, cod_first_impact, cod_second_impact, cod_third_impact, cod_one_hour_impact, cod_tow_hour_impact, cod_three_hour_impact]
            records.append(record)
            names.append(event)

        frame = pd.DataFrame(data = records, index=names, columns=["Count", "CoD Original Impact", "CoD First Impact", "CoD Second Impact", "CoD Third Impact", "CoD One Hour Impact", "CoD Tow Hour Impact", "CoD Three Hour Impact"])

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