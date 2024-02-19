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
            self.tradermate_token = os.getenv("TRADERMATE")

    def economic_calendar(self, start_date, end_date):
        """Get Economic Calendar"""
    
        endpoint = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={start_date}&to={end_date}&apikey={self.fmp_token}"    
        response = requests.get(endpoint)
        json_data = response.json()
        
        return json_data
    
    def foreign_exchange_rate_minute(self, timestamp, pair = "EURUSD", price = "close", source = "MetaTrader5"):
        """Get Price for Minute-Bar"""
        
        data = self.foreign_exchange_rate_influxdb(timestamp, pair, source)

        if type(data) == pd.core.frame.DataFrame and price in data and timestamp in data.index:
             return data.loc[timestamp][price]
        return None

    def foreign_exchange_rate_influxdb(self, timestamp, pair, source):
        """Get Foreign Exchange Rates from InfluxDB"""

        query_data = self.database.query_data(timestamp, pair, "1min", source=source)
        clean_data = self.database.preprocess_query_dataframe(query_data)

        return clean_data