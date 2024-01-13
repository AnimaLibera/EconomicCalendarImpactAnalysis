from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import requests
import sqlite3
import os

class Provider:

    def __init__(self):
          self.environment()

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

    def foreign_exchange_rates(self, start_date, end_date, pair = "EURUSD"):
        """Get Foreign Exchange Rates"""

        endpoint = f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{pair}?from={start_date}&to={end_date}&apikey={self.fmp_token}"
        response = requests.get(endpoint)
        json_data = response.json()

        return self.parse_fx_rates(json_data)
    
    def foreign_exchange_rates_timestamp(self, datetime = "2019-10-09-13:24", pair = "EURUSD"):
        """Get Foreign Exchange Rates by Timestamp for Minute-Bar"""

        endpoint = f"https://marketdata.tradermade.com/api/v1/minute_historical?currency={pair}&date_time={datetime}&api_key={self.tradermate_token}"
        response = requests.get(endpoint)
        json_data = response.json()
    
        return json_data
    
    def foreign_exchange_rate_minute_close(self, timestamp, pair = "EURUSD"):
        """Get Close for Minute-Bar"""
        
        datetime = timestamp.strftime("%Y-%m-%d-%H:%M")
        data = self.foreign_exchange_rates_timestamp(datetime, pair)
        
        if "close" in data:
             return data["close"]
        return None

    def parse_fx_rates(self, json_data):
        """Parse Foreign Exchange Rates"""
        rates = []
        datetime = []

        for element in json_data:
            rates.append(element["close"])
            datetime.append(pd.Timestamp(element["date"]))

        return pd.Series(data=rates, index=datetime)
    
    def foreign_exchange_rate_database(self, timestamp = pd.Timestamp("2020-01-02-06:00"), pair = "EURUSD"):
        """Get Foreign Exchange Rates from Database"""

        database = Database()
        bar = database.get_bar(timestamp, pair, "1min")
        print(bar)


    def load_csv_to_dataframe(self, relativ_file_path = "../Data/", file_name = "EURUSD_M1_GMT+2_2020-01-02-0600_2023-12-29-2358.csv"):
        """Load CSV to DataFrame"""
        
        data = pd.read_csv(relativ_file_path + file_name, sep="\t", index_col = None, parse_dates = True)
        return data

    def populate_database(self):
        """Populate Database with CSV Data"""

        data = self.load_csv_to_dataframe()
        database = Database()

        for index, row in data.iloc[:10].iterrows():
            timestampString = row["<DATE>"] + " " + row["<TIME>"]
            timestamp = datetime.strptime(timestampString, "%Y.%m.%d %H:%M:%S")
            bar = {}
            bar["timestamp"] = timestamp
            bar["symbol"] = "EURUSD"
            bar["timeframe"] = "1min"
            bar["open"] = row["<OPEN>"]
            bar["high"] = row["<HIGH>"]
            bar["low"] = row["<LOW>"]
            bar["close"] = row["<CLOSE>"]
            bar["spread"] = row["<SPREAD>"]

            database.insert_bar(bar)

class Database():
    """Class to fetch and update SQLite3 Bar Data"""

    def __init__(self, relative_path = "../Data/", file_name = "market.db"):
        """Constructors creates Connection to SQLite3 Database"""
        self.full_relativ_path = relative_path + file_name
        self.create_connection()

    def create_connection(self):
        """Create Connection to SQLite3 Database"""
        self.connection = sqlite3.connect(self.full_relativ_path)

    def create_table(self):
        command = """   CREATE TABLE IF NOT EXISTS bars(
                        timestamp TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        open REAL NOT NULL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL NOT NULL,
                        spread INTEGER NOT NULL,
                        PRIMARY KEY(timestamp,symbol,timeframe)
                        );""" #Timestamp ISO8601 YYYY-MM-DD HH:MM:SS.SSSSSS
        cursor = self.connection.cursor()
        cursor.execute(command)    

    def drop_table(self):
        command = "DROP TABLE IF EXISTS bars"
        cursor = self.connection.cursor()
        cursor.execute(command)

    def print_first_last(self):
        """Print First and Last Bar in Database"""
        command = "SELECT * FROM bars;"
        cursor = self.connection.cursor()
        cursor.execute(command)
        result = cursor.fetchall()
        print("Printing first and last Bars in Database:")
        print(result[0])
        print(result[-1])

    def insert_bar(self, bar):
        command = 'INSERT INTO bars(timestamp,symbol,timeframe,open,high,low,close,spread) VALUES(?,?,?,?,?,?,?,?)'
        timestamp = bar["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")
        parameters = (timestamp,bar["symbol"],bar["timeframe"],bar["open"],bar["high"],bar["low"],bar["close"],bar["spread"])
        cursor = self.connection.cursor()
        cursor.execute(command, parameters)
        self.connection.commit()

    def get_bar(self, timestamp, symbol, timeframe):
        timestampString = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
        try:
            command = "SELECT * FROM bars WHERE timestamp=? AND symbol=? AND timeframe=?;"
            cursor = self.connection.cursor()
            cursor.execute(command, (timestampString, symbol, timeframe))
            result = cursor.fetchone()
            bar = {}
            bar["timestamp"] = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f")
            bar["symbol"] = result[1]
            bar["timeframe"] = result[2]
            bar["open"] = result[3]
            bar["high"] = result[4]
            bar["low"] = result[5]
            bar["close"] = result[6]
            bar["spread"] = result[7]
            return bar
        except:
            bar = {}
            bar["timestamp"] = timestamp
            bar["symbol"] = symbol
            bar["timeframe"] = timeframe
            bar["open"] = None
            bar["high"] = None
            bar["low"] = None
            bar["close"] = None
            bar["spread"] = None
            return bar

if __name__ == "__main__":
    database = Database()
    database.print_first_last()

    #database.drop_table()
    #database.create_table()

    provider = Provider()
    provider.foreign_exchange_rate_database()
    #provider.populate_database()