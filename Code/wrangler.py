from datetime import datetime
import pandas as pd
import pytz

class ForexTester:
    """ForexTester.com Dataprovider"""

    def load_csv_to_dataframe(self, relativ_file_path = "../Data/", file_name = "ForexTester.com EURUSD 1MIN GMT 2001-01-01 2024-01-31.txt"):
        """Load CSV to DataFrame"""
        
        data = pd.read_csv(relativ_file_path + file_name, sep=",", index_col = None, parse_dates = False, dtype = {"<DTYYYYMMDD>": str, "<TIME>": str})
        return data
    
    def process_timeframe_csv_dataframe(self, data):
        """Process only Timeframe for raw CSV Dataframe"""
        data["timestamp"] = (data["<DTYYYYMMDD>"] + " " + data["<TIME>"]).apply(lambda string: datetime.strptime(string, "%Y%m%d %H%M%S"))
        data.set_index("timestamp", inplace = True)

        return data

    def preprocess_csv_dataframe(self, data, symbol, timeframe = "1min", timezone = "Etc/GMT", source = "ForexTester.com"):
        """Preprocess CSV Dataframe: timezone is pytz Timezone"""

        tz = pytz.timezone(timezone)
        data["timestamp"] = (data["<DTYYYYMMDD>"] + " " + data["<TIME>"]).apply(lambda string: datetime.strptime(string, "%Y%m%d %H%M%S").replace(tzinfo=tz))
        data["symbol"] = symbol
        data["timeframe"] = timeframe
        data["source"] = source
        data.drop(columns = ["<TICKER>", "<DTYYYYMMDD>", "<TIME>", "<VOL>",], inplace = True)
        data.columns = ["open", "high", "low", "close", "timestamp", "symbol", "timeframe", "source"]
        data.set_index("timestamp", inplace = True)

        return data

    def populate_csv_file(self, data, relativ_file_path = "../Data/", file_name = "market.csv"):

        data.to_csv(relativ_file_path + file_name, sep = ",", index = False)