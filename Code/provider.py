from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import requests
import influx
import pytz
import os

class Provider:

    def __init__(self):
          self.environment()

    def environment(self):
            """Load Environment from File"""
            load_dotenv("../Secrets/Tokens.env")
            self.fmp_token = os.getenv("FMP")
            self.tradermate_token = os.getenv("TRADERMATE")

    def economic_calendar(self, start_date, end_date):
        """Get Economic Calendar"""
    
        endpoint = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={start_date}&to={end_date}&apikey={self.fmp_token}"    
        response = requests.get(endpoint)
        json_data = response.json()
        
        return json_data

    def foreign_exchange_rates(self, start_date, end_date, pair = "EURUSD"):
        """Get Foreign Exchange Rates"""

        endpoint = f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{pair}?from={start_date}&to={end_date}&apikey={self.fmp_token}"
        response = requests.get(endpoint)
        json_data = response.json()

        return self.parse_fx_rates(json_data)
    
    def foreign_exchange_rates_timestamp(self, datetime = "2019-10-09-13:24", pair = "EURUSD"):
        """Get Foreign Exchange Rates by Timestamp for Minute-Bar"""

        endpoint = f"https://marketdata.tradermade.com/api/v1/minute_historical?currency={pair}&date_time={datetime}&api_key={self.tradermate_token}"
        response = requests.get(endpoint)
        json_data = response.json()
    
        return json_data
    
    def foreign_exchange_rate_minute_close(self, timestamp, pair = "EURUSD"):
        """Get Close for Minute-Bar"""
        
        #datetime = timestamp.strftime("%Y-%m-%d-%H:%M")
        print(timestamp)
        #data = self.foreign_exchange_rate_database(timestamp, pair)
        data = self.foreign_exchange_rate_influxdb(timestamp, pair)

        #print(data)

        if type(data) == pd.core.frame.DataFrame and "close" in data and timestamp in data.index:
             return data.loc[timestamp]["close"]
        return None

    def foreign_exchange_rate_influxdb(self, timestamp, pair):
        """Get Foreign Exchange Rates from InfluxDB"""

        database = influx.InfluxDatabase()
        query_data = database.query_data(timestamp, pair, "1min")
        clean_data = database.preprocess_query_dataframe(query_data)

        return clean_data

    def parse_fx_rates(self, json_data):
        """Parse Foreign Exchange Rates"""
        rates = []
        datetime = []

        for element in json_data:
            rates.append(element["close"])
            datetime.append(pd.Timestamp(element["date"]))

        return pd.Series(data=rates, index=datetime)
    
    def foreign_exchange_rate_database(self, timestamp = pd.Timestamp("2020-01-02-06:00"), pair = "EURUSD"):
        """Get Foreign Exchange Rates from Database"""

        database = Database()
        bar = database.get_bar(timestamp, pair, "1min")
        
        return bar

    def print_cycle_dataframe(self, data):

        for index, row in data.iterrows():
            print(index, row)