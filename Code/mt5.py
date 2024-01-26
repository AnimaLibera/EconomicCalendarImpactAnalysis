from datetime import datetime
import pandas as pd
import pytz

class MetaTrader5:
    """MetaTrader5 Dataprovider"""

    def load_csv_to_dataframe(self, relativ_file_path = "../Data/", file_name = "EURUSD_M1_GMT+2_202401020000_202401260000.csv"):
        """Load CSV to DataFrame"""
        
        data = pd.read_csv(relativ_file_path + file_name, sep="\t", index_col = None, parse_dates = False)
        return data

    def preprocess_csv_dataframe(self, data, symbol = "EURUSD", timeframe = "1min", timezone = "Etc/GMT+2"):
        """Preprocess CSV Dataframe: timezone is pytz Timezone"""

        tz = pytz.timezone(timezone)
        data["timestap"] = (data["<DATE>"] + " " + data["<TIME>"]).map(lambda string: datetime.strptime(string, "%Y.%m.%d %H:%M:%S").replace(tzinfo=tz))
        data["symbol"] = symbol
        data["timeframe"] = timeframe
        data.drop(columns = ["<DATE>", "<TIME>", "<TICKVOL>", "<VOL>"], inplace = True)
        data.columns = ["open", "high", "low", "close", "spread", "timestamp", "symbol", "timeframe"]
        data.set_index("timestamp", inplace = True)

        return data

    def populate_csv_file(self, data, relativ_file_path = "../Data/", file_name = "market.csv"):

        data.to_csv(relativ_file_path + file_name, sep = "\t", index = True)

if __name__ == "__main__":

    mt5 = MetaTrader5()
    print("Step #1")
    raw_data = mt5.load_csv_to_dataframe()
    print("Step #2")
    clean_data = mt5.preprocess_csv_dataframe(raw_data)
    print("Step #3")
    mt5.populate_csv_file(clean_data)