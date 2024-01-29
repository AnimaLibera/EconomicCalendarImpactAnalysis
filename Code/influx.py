import influxdb_client as db
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import pandas as pd
import os

class InfluxDatabase:
    """Class to work with Influx-Database"""

    def __init__(self, deployment="local"):
        self.deplyoment = deployment
        self.environment()
        self.client = db.InfluxDBClient(url=self.influx_url, token=self.influx_token, org=self.influx_organisation, debug=False)
        #self.write_api = self.client.write_api(write_options=db.WriteOptions(batch_size=5_000, flush_interval=1_000))
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
    
    def environment(self):
        """Load Environment from File or Secerets"""
        if self.deplyoment == "local":
            load_dotenv("../Secrets/Tokens.env")
            self.influx_token = os.getenv("INFLUX_TOKEN")
            self.influx_organisation = os.getenv("INFLUX_ORGANISATION")
            self.infux_bucket = os.getenv("INFLUX_BUCKET")
            self.influx_url = os.getenv("INFLUX_URL")
        elif self.deplyoment == "streamlit":
            self.influx_token = os.environ("INFLUX_TOKEN")
            self.influx_organisation = os.environ("INFLUX_ORGANISATION")
            self.infux_bucket = os.environ("INFLUX_BUCKET")
            self.influx_url = os.environ("INFLUX_URL")

    def ingest_data(self, data_frame, measurement_name = "prices", tag_columns = ["symbol", "timeframe"]):
        """Ingest stepwise Data into InfluxDB"""

        row_numbers = data_frame.shape[0]
        step = 5000
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

    def ingest_events(self, data_frame, measurement_name = "events", tag_columns = ["currency", "impact"]):
        """Call ingest_data with right Arguments to ingest Events into InfluxDB"""

        self.ingest_data(data_frame, measurement_name, tag_columns)

    def query_data(self, time = pd.Timestamp("2024-01-25T13:30"), symbol = "EURUSD", timeframe = "1min"):
        """Query Pricedata from InfluxDB"""

        unix_start = int(time.timestamp())
        unix_stop = int((time + pd.Timedelta(minutes=1)).timestamp())

        query = f"""
            from(bucket: "{self.infux_bucket}")
            |> range(start: {unix_start}, stop: {unix_stop})
            |> filter(fn: (r) => r._measurement == "prices")
            |> filter(fn: (r) => r.symbol == "{symbol}")
            |> filter(fn: (r) => r.timeframe == "{timeframe}")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """

        return self.query_api.query_data_frame(query)

    def query_events(self, start = pd.Timestamp("2024-01-01T00:00"), stop = pd.Timestamp("2024-01-26T00:00"), currency = "USD", impact = "High"):
        """Query Events from InfluxDB"""

        unix_start = int(start.timestamp())
        unix_stop = int((stop.timestamp()))

        query = f"""
            from(bucket: "{self.infux_bucket}")
            |> range(start: {unix_start}, stop: {unix_stop})
            |> filter(fn: (r) => r._measurement == "events")
            |> filter(fn: (r) => r.currency == "{currency}")
            |> filter(fn: (r) => r.impact == "{impact}")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """

        return self.query_api.query_data_frame(query)

    def preprocess_query_dataframe(self, data_frame):
        """Preprocess Query Dataframe"""

        if data_frame.empty:
            return None

        data_frame.drop(columns = ["result", "table", "_measurement", "_start", "_stop"], inplace = True)
        data_frame.rename(columns={"_time": "timestamp"}, inplace = True)
        data_frame.set_index("timestamp", inplace = True)

        return data_frame


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
        db = InfluxDatabase()
        query_data = db.query_data()
        print(query_data)
        clean_data = db.preprocess_query_dataframe(query_data)
        print(clean_data)