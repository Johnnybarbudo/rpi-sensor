import os
import time
import json
import yaml
from pathlib import Path
from google.cloud import pubsub_v1
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get("INFLUXDB_TOKEN")
org = "simon@raiz.farm"
url = "https://europe-west1-1.gcp.cloud2.influxdata.com"
bucket = "farm-1-lisbon"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)


class Publisher:
    def __init__(self):
        self.load_config()
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)

    def load_config(self):
        with open(Path(__file__).parent.joinpath("device_config.yaml"), "r") as ymlfile:
            config_values = yaml.load(ymlfile, Loader=yaml.FullLoader)
            for config_key in config_values:
                setattr(self, config_key, config_values[config_key])

    def publish(self, data, data_type):
        data_to_publish = json.dumps(data).encode("utf-8")
        self.publisher.publish(
            self.topic_path,
            data_to_publish,
            device_id=self.device_id,
            device_type=data_type,
            dataset_id=self.dataset_id,
        )

        point = Point(data_type).tag("farm_id", self.dataset_id).tag("device_id", self.device_id)

        for key in data[0]:
            point = point.field(key, round(data[0][key], 3))

        write_api.write(bucket=bucket, org="simon@raiz.farm", record=point)
