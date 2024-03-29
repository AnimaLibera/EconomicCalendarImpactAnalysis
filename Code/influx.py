#import influxdb_client as db
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import influxdb_client as db
import pandas as pd
import streamlit as st
import os

class InfluxDatabase:
    """Class to work with Influx-Database"""

    def __init__(self, deployment = "local"):
        self.deployment = deployment
        self.environment()
        self.client = db.InfluxDBClient(url=self.influx_url, token=self.influx_token, org=self.influx_organisation, debug=False)
        self.write_api_batch = self.client.write_api(write_options=db.WriteOptions(batch_size=5_000, flush_interval=1_000))
        self.write_api_synch = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def __del__(self):
        self.write_api_batch.__del__()
        self.write_api_synch.__del__()
        self.query_api.__del__()
        self.client.__del__()
    
    def environment(self):
        """Load Environment from File or Secerets"""
        if self.deployment == "local":
            load_dotenv("../Secrets/Tokens.env")
            self.influx_token = os.getenv("INFLUX_TOKEN")
            self.influx_organisation = os.getenv("INFLUX_ORGANISATION")
            self.infux_bucket = os.getenv("INFLUX_BUCKET")
            self.influx_url = os.getenv("INFLUX_URL")
        elif self.deployment == "streamlit":
            self.influx_token = st.secrets["INFLUX_TOKEN"]
            self.influx_organisation = st.secrets["INFLUX_ORGANISATION"]
            self.infux_bucket = st.secrets["INFLUX_BUCKET"]
            self.influx_url = st.secrets["INFLUX_URL"]
        elif self.deployment == "linode":
            self.influx_token = st.secrets["LINODE_INFLUX_TOKEN"]
            self.influx_organisation = st.secrets["LINODE_INFLUX_ORGANISATION"]
            self.infux_bucket = st.secrets["LINODE_INFLUX_BUCKET"]
            self.influx_url = st.secrets["LINODE_INFLUX_URL"]

    def ingest_data(self, data_frame, measurement_name = "prices", tag_columns = ["symbol", "timeframe", "source"], mode="live"):
        """Ingest stepwise Data into InfluxDB"""
        
        if mode == "test":
            self.write_api_synch.write(self.infux_bucket, self.influx_organisation, record = data_frame.iloc[0:10], data_frame_measurement_name = measurement_name, data_frame_tag_columns = tag_columns)
            return  

        if mode == "batch":
            self.write_api_batch.write(self.infux_bucket, self.influx_organisation, record = data_frame, data_frame_measurement_name = measurement_name, data_frame_tag_columns = tag_columns)
            return
        
        if mode == "live":
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

                self.write_api_synch.write(self.infux_bucket, self.influx_organisation, record = data_frame.iloc[start:stop], data_frame_measurement_name = measurement_name, data_frame_tag_columns = tag_columns)

                start += step
                counter += 1

    def ingest_events(self, data_frame, measurement_name = "events", tag_columns = ["currency", "impact", "source"]):
        """Call ingest_data with right Arguments to ingest Events into InfluxDB"""

        self.ingest_data(data_frame, measurement_name, tag_columns)

    def query_data(self, time = pd.Timestamp("2024-01-25T13:30"), symbol = "EURUSD", timeframe = "1min", source = "MetaTrader5"):
        """Query Pricedata from InfluxDB"""

        unix_start = int(time.timestamp())
        unix_stop = int((time + pd.Timedelta(minutes=1)).timestamp())

        query = f"""
            from(bucket: "{self.infux_bucket}")
            |> range(start: {unix_start}, stop: {unix_stop})
            |> filter(fn: (r) => r._measurement == "prices")
            |> filter(fn: (r) => r.symbol == "{symbol}")
            |> filter(fn: (r) => r.timeframe == "{timeframe}")
            |> filter(fn: (r) => r.source == "{source}")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """

        return self.query_api.query_data_frame(query)

    def query_events(self, start = pd.Timestamp("2024-01-01T00:00"), stop = pd.Timestamp("2024-01-26T00:00"), currency = "USD", impact = "High", source = "FinancialModelingPrep"):
        """Query Events from InfluxDB"""

        unix_start = int(start.timestamp())
        unix_stop = int((stop.timestamp()))

        query = f"""
            from(bucket: "{self.infux_bucket}")
            |> range(start: {unix_start}, stop: {unix_stop})
            |> filter(fn: (r) => r._measurement == "events")
            |> filter(fn: (r) => r.currency == "{currency}")
            |> filter(fn: (r) => r.impact == "{impact}")
            |> filter(fn: (r) => r.source == "{source}")
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