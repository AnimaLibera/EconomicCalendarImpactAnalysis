from dotenv import load_dotenv
from datetime import datetime
import streamlit as st
import pandas as pd
import requests
import influx
import pytz
import os

class Provider:

    def __init__(self, deployment = "local"):
        self.deployment = deployment
        self.environment()
        self.database = influx.InfluxDatabase(deployment = deployment)

    def environment(self):
        """Load Environment from File or Secerets"""
        if self.deployment == "local":
            load_dotenv("../Secrets/Tokens.env")
            self.fmp_token = os.getenv("FMP")
            self.tradermade_token = os.getenv("TRADERMADE")
        elif self.deployment == "streamlit":
            self.fmp_token = st.secrets["FMP"]
            self.tradermade_token = st.secrets["TRADERMADE"]
        elif self.deployment == "linode":
            self.fmp_token = st.secrets["FMP"]
            self.tradermade_token = st.secrets["TRADERMADE"]

    def economic_calendar(self, start_date, end_date):
        """Get Economic Calendar"""
    
        endpoint = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={start_date}&to={end_date}&apikey={self.fmp_token}"    
        response = requests.get(endpoint)
        json_data = response.json()
        
        return json_data
    
    def foreign_exchange_rate_minute(self, timestamp, pair = "EURUSD", price = "close", source = "MetaTrader5"):
        """Get Price for Minute-Bar"""
        
        if source in ["Dukascopy", "MetaTrader4", "Axiory.com", "MetaTrader5", "ForexTester.com"]:
            data = self.foreign_exchange_rate_influxdb(timestamp, pair, source)
            print(f"Try to call InfluxDB for Price Data, Result {data}")
            if type(data) == pd.core.frame.DataFrame and price in data and timestamp in data.index:
                return data.loc[timestamp][price]
            return None

        elif source == "TradeMade":
            data = self.foreign_exchange_rate_influxdb(timestamp, pair, source)
            if type(data) == pd.core.frame.DataFrame and price in data and timestamp in data.index:
                return data.loc[timestamp][price]
            else:
                return None
                try:
                    print("Try to call TradeMade API for Price Data")
                    data = self.foreign_exchange_rate_trademade(timestamp, pair, price)
                    dictornary = {
                                "symbol": pair,
                                "timeframe": "1min",
                                "source": source,
                                "open": data["open"],
                                "high": data["high"],
                                "low": data["low"],
                                "close": data["close"],
                    }
                    dataframe = pd.DataFrame(dictornary, index=[timestamp])
                    self.database.ingest_data(dataframe)
                    return data[price]
                except:
                    return None

    def foreign_exchange_rate_influxdb(self, timestamp, pair, source):
        """Get Foreign Exchange Rates from InfluxDB"""

        query_data = self.database.query_data(timestamp, pair, "1min", source=source)
        clean_data = self.database.preprocess_query_dataframe(query_data)

        return clean_data
    
    def foreign_exchange_rate_trademade(self, timestamp, pair, price):
        """Get Foreign Exchange Rates from TradeMade"""
        #TradeMade Timestamps are in UTC
        
        date_time = timestamp.strftime("%Y-%m-%d-%H:%M")
        endpoint = f"https://marketdata.tradermade.com/api/v1/minute_historical?currency={pair}&date_time={date_time}&api_key={self.tradermade_token}"
        
        response = requests.get(endpoint)
        json_data = response.json()
        return json_data