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

class Axiory:
    """Axiory.com Dataprovider"""

    def load_csv_to_dataframe(self, relativ_file_path = "../Data/Axiory/", file_name = "EURUSD_2023_all.csv"):
        """Load CSV to DataFrame"""
        
        data = pd.read_csv(relativ_file_path + file_name, sep=",", index_col = None, parse_dates = False)
        return data

    def preprocess_csv_dataframe(self, data, symbol, timeframe = "1min", timezone = "Etc/GMT-2", source = "Axiory.com"):
        """Preprocess CSV Dataframe: timezone is pytz Timezone"""

        data.columns = ["date", "time", "open", "high", "low", "close", "volume"]

        tz = pytz.timezone(timezone)
        data["timestamp"] = (data["date"] + " " + data["time"]).apply(lambda string: datetime.strptime(string, "%Y.%m.%d %H:%M").replace(tzinfo=tz))
        data["symbol"] = symbol
        data["timeframe"] = timeframe
        data["source"] = source
        data.drop(columns = ["date", "time", "volume",], inplace = True)
        data.set_index("timestamp", inplace = True)

        return data

    def populate_csv_file(self, data, relativ_file_path = "../Data/Axiory/", file_name = "market.csv"):

        data.to_csv(relativ_file_path + file_name, sep = ",", index = False)

class MetaTrader4:
    """MetaTrader4 Dataprovider"""

    def load_csv_to_dataframe(self, relativ_file_path = "../Data/MetaTrader4/", file_name = "MetaTrader4 EURUSD 1Min 3 Years History.csv"):
        """Load CSV to DataFrame"""
        
        data = pd.read_csv(relativ_file_path + file_name, sep=",", index_col = None, parse_dates = False)
        return data

    def preprocess_csv_dataframe(self, data, symbol, timeframe = "1min", timezone = "Etc/GMT-2", source = "MetaTrader4"):
        """Preprocess CSV Dataframe: timezone is pytz Timezone"""

        data.columns = ["date", "time", "open", "high", "low", "close", "volume"]

        tz = pytz.timezone(timezone)
        data["timestamp"] = (data["date"] + " " + data["time"]).apply(lambda string: datetime.strptime(string, "%Y.%m.%d %H:%M").replace(tzinfo=tz))
        data["symbol"] = symbol
        data["timeframe"] = timeframe
        data["source"] = source
        data.set_index("timestamp", inplace = True)
        data.drop(columns = ["date", "time", "volume"], inplace = True)

        return data

class Dukascopy:
    """Dukascopy Dataprovider"""

    def load_csv_to_dataframe(self, relativ_file_path = "../Data/Dukascopy/", file_name = "Dukascopy EURUSD 2023-01-01 2023-12-31.csv"):
        """Load CSV to DataFrame"""
        
        data = pd.read_csv(relativ_file_path + file_name, sep=",", index_col = "Gmt time", parse_dates = ["Gmt time"], date_format={"Gmt time": "%d.%m.%Y %H:%M:%S.%f"})
        return data

    def preprocess_csv_dataframe(self, data, symbol, timeframe = "1min", timezone = "Etc/GMT", source = "Dukascopy"):
        """Preprocess CSV Dataframe: timezone is pytz Timezone"""

        tz = pytz.timezone(timezone)
        data.index = data.index.tz_localize(tz)
        data["symbol"] = symbol
        data["timeframe"] = timeframe
        data["source"] = source
        data.drop(columns = ["Volume"], inplace = True)
        data.columns = ["open", "high", "low", "close", "symbol", "timeframe", "source"]
        data.index.name = "timestamp"

        return data