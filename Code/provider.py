from dotenv import load_dotenv
import pandas as pd
import requests
import os

class Provider:

    def __init__(self):
          self.environment()

    def environment(self):
            """Load Environment from File"""
            load_dotenv("../Secrets/Tokens.env")
            self.fmp_token = os.getenv("FMP")

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
    
    def parse_fx_rates(self, json_data):
        """Parse Foreign Exchange Rates"""
        rates = []
        datetime = []

        for element in json_data:
            rates.append(element["close"])
            datetime.append(element["date"])

        return pd.Series(data=rates, index=datetime)