from datetime import datetime
import pandas as pd
import pytz

class MetaTrader5:
    """MetaTrader5 Dataprovider"""

    def load_csv_to_dataframe(self, relativ_file_path = "../Data/", file_name = "EURUSD_M1_GMT+2_202401020000_202401260000.csv"):
        """Load CSV to DataFrame"""
        
        data = pd.read_csv(relativ_file_path + file_name, sep="\t", index_col = None, parse_dates = False)
        return data

    def preprocess_csv_dataframe(self, data, symbol, timeframe = "1min", timezone = "Etc/GMT+2", source = "MetaTrader5"):
        """Preprocess CSV Dataframe: timezone is pytz Timezone"""

        tz = pytz.timezone(timezone)
        data["timestamp"] = (data["<DATE>"] + " " + data["<TIME>"]).apply(lambda string: datetime.strptime(string, "%Y.%m.%d %H:%M:%S").replace(tzinfo=tz))
        data["symbol"] = symbol
        data["timeframe"] = timeframe
        data["source"] = source
        data.drop(columns = ["<DATE>", "<TIME>", "<TICKVOL>", "<VOL>",], inplace = True)
        data.columns = ["open", "high", "low", "close", "spread", "timestamp", "symbol", "timeframe", "source"]
        data.set_index("timestamp", inplace = True)

        return data

    def populate_csv_file(self, data, relativ_file_path = "../Data/", file_name = "market.csv"):

        data.to_csv(relativ_file_path + file_name, sep = "\t", index = True)