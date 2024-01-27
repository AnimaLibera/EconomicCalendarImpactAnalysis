from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import influx
import requests
import pytz
import os

class FinancialModelingPrep:
    """Financial Modeling Prep Dataprovider"""

    def __init__(self):
        self.environment()
        self.database = influx.InfluxDatabase()

    def environment(self):
            """Load Environment from File"""
            load_dotenv("../Secrets/Tokens.env")
            self.fmp_token = os.getenv("FMP")
    
    def economic_calendar(self, start_date, end_date):
        """Get Economic Calendar"""
        
        start_string = start_date.strftime("%Y-%m-%d")
        stop_string = end_date.strftime("%Y-%m-%d")

        endpoint = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={start_string}&to={stop_string}&apikey={self.fmp_token}"    
        response = requests.get(endpoint)
        json_data = response.json()
        
        return json_data

    def parse_economic_calendar_to_dataframe(self, json_data):
        """Parse Economic Calendar from JSON to Dataframe"""

        data_frame = pd.DataFrame(json_data)

        return data_frame
    
    def preprocess_economic_calendar(self, data_frame):
        """Preprocess Economic Calendar"""

        data_frame["timestamp"] = data_frame["date"].apply(lambda element: pd.Timestamp(element).tz_localize(tz="Etc/GMT"))
        data_frame.set_index("timestamp", inplace=True)
        data_frame.drop(columns=["date", "country", "previous", "change", "changePercentage"], inplace=True)
        data_frame["event"] = data_frame["event"].apply(self.clean_event)

        return data_frame
    
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
        
    def economic_calendar_pipeline(self, start_date, end_date):
        """Pipeline to wrangle Economic Calendar from Soure to Sink
            Source: financialmodelingprep.com
            Sink:   Local influx Database"""
        
        print("Getting Economic Calendar")
        json_data = self.economic_calendar(start_date, end_date)
        
        print("Parsing Economic Calendar")
        data_frame = self.parse_economic_calendar_to_dataframe(json_data)
        
        print("Preprocessing Economic Calendar")
        nice_df = self.preprocess_economic_calendar(data_frame)

        print("Ingesting Economic Calendar")
        self.database.ingest_events(nice_df)

if __name__ == "__main__":
    
    if False:
        start_date = "2023-01-01"
        stop_date = "2024-01-01"

        FMP = FinancialModelingPrep()
        json_data = FMP.economic_calendar(start_date, stop_date)
        df = FMP.parse_economic_calendar_to_dataframe(json_data)
        nice_df = FMP.preprocess_economic_calendar(df)
        DB = influx.InfluxDatabase()
        DB.ingest_events(nice_df)
        print(nice_df)
     
    if True:
        DB = influx.InfluxDatabase()
        data = DB.query_events(currency="JPY", impact="Medium")
        nice_data = DB.preprocess_query_dataframe(data)
        print(nice_data)