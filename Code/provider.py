from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import requests
import influx
import pytz
import os

class Provider:

    def __init__(self, deployment = "local"):
          self.environment()
          self.database = influx.InfluxDatabase(deployment = deployment)

    def environment(self):
            """Load Environment from File"""
            load_dotenv("../Secrets/Tokens.env")
            self.fmp_token = os.getenv("FMP")
            self.tradermade_token = os.getenv("TRADERMADE")

    def economic_calendar(self, start_date, end_date):
        """Get Economic Calendar"""
    
        endpoint = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={start_date}&to={end_date}&apikey={self.fmp_token}"    
        response = requests.get(endpoint)
        json_data = response.json()
        
        return json_data
    
    def foreign_exchange_rate_minute(self, timestamp, pair = "EURUSD", price = "close", source = "MetaTrader5"):
        """Get Price for Minute-Bar"""
        
        if source == "MetaTrader5":
            data = self.foreign_exchange_rate_influxdb(timestamp, pair, source)
            if type(data) == pd.core.frame.DataFrame and price in data and timestamp in data.index:
                return data.loc[timestamp][price]
            return None

        elif source == "TradeMade":
            data = self.foreign_exchange_rate_influxdb(timestamp, pair, source)
            if type(data) == pd.core.frame.DataFrame and price in data and timestamp in data.index:
                return data.loc[timestamp][price]
            else:
                try:
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