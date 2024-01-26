from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import requests
import pytz
import os

class FinancialModelingPrep:
    """Financial Modeling Prep Dataprovider"""

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

if __name__ == "__main__":
     
    start_date = "2024-01-01"
    stop_date = "2024-01-25"

    FMP = FinancialModelingPrep()
    json_data = FMP.economic_calendar(start_date, stop_date)
    df = FMP.parse_economic_calendar_to_dataframe(json_data)
    nice_df = FMP.preprocess_economic_calendar(df)
    print(nice_df)
     