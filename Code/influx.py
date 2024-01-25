import influxdb_client as db
from influxdb_client.client.write_api import ASYNCHRONOUS
from dotenv import load_dotenv
import pandas as pd
import os

class InfluxDatabase:
    """Class to work with Influx-Database"""

    def __init__(self):
        self.environment()
        self.influx_organisation = "NaturalPerson"
        self.infux_bucket = "Market2"
        self.influx_url = "http://localhost:8086"
        self.client = db.InfluxDBClient(url=self.influx_url, token=self.influx_token, org=self.influx_organisation)
        self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
    
    def environment(self):
        """Load Environment from File"""
        load_dotenv("../Secrets/Tokens.env")
        self.influx_token = os.getenv("INFLUX")

    def ingest_data(self, data_frame, measurement_name = "prices2", tag_columns = ["symbol", "timeframe"]):
         """Ingest Data into InfluxDB"""

         self.write_api.write(self.infux_bucket, self.influx_organisation, record = data_frame, data_frame_measurement_name = measurement_name, data_frame_tag_columns = tag_columns)

if __name__ == "__main__":
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