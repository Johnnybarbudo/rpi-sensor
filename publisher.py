import json
import yaml
from pathlib import Path
from google.cloud import pubsub_v1


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
