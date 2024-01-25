from sqlalchemy import create_engine
import pandas as pd
import sqlite3


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