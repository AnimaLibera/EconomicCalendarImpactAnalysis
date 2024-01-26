import influxdb_client as db
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import pandas as pd
import os

class InfluxDatabase:
    """Class to work with Influx-Database"""

    def __init__(self):
        self.environment()
        self.influx_organisation = "NaturalPerson"
        self.infux_bucket = "NewMarket"
        self.influx_url = "http://localhost:8086"
        self.client = db.InfluxDBClient(url=self.influx_url, token=self.influx_token, org=self.influx_organisation, debug=False)
        self.write_api = self.client.write_api(write_options=db.WriteOptions(batch_size=5_000, flush_interval=1_000))
        self.query_api = self.client.query_api()
    
    def environment(self):
        """Load Environment from File"""
        load_dotenv("../Secrets/Tokens.env")
        self.influx_token = os.getenv("INFLUX")

    def ingest_data(self, data_frame, measurement_name = "prices", tag_columns = ["symbol", "timeframe"]):
        """Ingest stepwise Data into InfluxDB"""

        row_numbers = data_frame.shape[0]
        step = row_numbers // 10
        start = 0
        stop = 0
        counter = 1

        while stop < row_numbers:

            stop += step

            if stop > row_numbers:
                stop = row_numbers

            print(f"Counter: {counter}, Start at: {start}, Stop at: {stop}")

            self.write_api.write(self.infux_bucket, self.influx_organisation, record = data_frame.iloc[start:stop], data_frame_measurement_name = measurement_name, data_frame_tag_columns = tag_columns)

            start += step
            counter += 1

    def query_data(self, start = pd.Timestamp("2023-12-01T00"), stop = pd.Timestamp("2024-01-01T00"), symbol = "EURUSD", timeframe = "1min"):
        """Query Pricedata from InfluxDB"""

        unix_start = int(start.timestamp())
        unix_stop = int(stop.timestamp())

        query = f"""
            from(bucket: "{self.infux_bucket}")
            |> range(start: {unix_start}, stop: {unix_stop})
            |> filter(fn: (r) => r._measurement == "prices")
            |> filter(fn: (r) => r.symbol == "{symbol}")
            |> filter(fn: (r) => r.timeframe == "{timeframe}")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """

        return self.query_api.query_data_frame(query)

if __name__ == "__main__":
    
    if False:
        import mt5
        print("Step #0")
        metatrader = mt5.MetaTrader5()
        print("Step #1")
        raw_data = metatrader.load_csv_to_dataframe()
        print("Step #2")
        clean_data = metatrader.preprocess_csv_dataframe(raw_data)
        print("Step #3")
        database = InfluxDatabase()
        print("Step #4")
        database.ingest_data(clean_data)
    
    if True:
        print("Query Data")
        query_data = InfluxDatabase().query_data()
        print(query_data)