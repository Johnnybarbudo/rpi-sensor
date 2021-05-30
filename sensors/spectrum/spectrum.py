import yaml
import json
from pathlib import Path
from time import sleep
from datetime import datetime, timezone
from sensors.spectrum.as7341 import get_sensor
from sensors.spectrum.constants import CONST
from adafruit_as7341 import Gain


class SpectrumSensor:
    def __init__(self):
        self.sensor = get_sensor()
        self.sensor.gain = 7
        self.load_config()

    def update_tint(self):
        self.integration_time = ((self.sensor.atime + 1) * (self.sensor.astep + 1) * 2.78) / 1000
        print(f"New integration time: {round(self.integration_time, 2)} ms")

    def load_config(self):
        with open(Path(__file__).parent.joinpath("spectrum_config.yaml"), "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

        if cfg["atime"] != self.sensor.atime:
            self.sensor.atime = cfg["atime"]
            sleep(0.2)
            self.update_tint()

        if cfg["astep"] != self.sensor.astep:
            self.sensor.astep = cfg["astep"]
            sleep(0.2)
            self.update_tint()

    def tune_gain(self):
        """
        Change gain if needed based on channel_CLEAR, as this will likely have the greatest value
        """
        min_threshold = 1000
        max_threshold = 50000
        if self.sensor.channel_CLEAR < min_threshold and self.sensor.gain != 10:
            while self.sensor.channel_CLEAR < min_threshold:
                self.sensor.all_channels
                if self.sensor.gain < 10:
                    self.sensor.gain += 1
                    print(f"Raised gain to {Gain.string[self.sensor.gain]}X")
                    sleep(0.2)
                else:
                    print("Gain at maximum, cannot increase anymore")
                    break

        if self.sensor.channel_CLEAR > max_threshold and self.sensor.gain != 0:
            while self.sensor.channel_CLEAR > max_threshold:
                self.sensor.all_channels
                if self.sensor.gain > 0:
                    self.sensor.gain -= 1
                    print(f"Lowered gain to {Gain.string[self.sensor.gain]}")
                    sleep(0.2)
                else:
                    print("Gain at minimum, cannot decrease anymore")
                    break

    def measure(self):
        self.load_config()  # Load config here, so it can be changed without restarting
        self.tune_gain()

        row = {
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "sensor_config": json.dumps(
                {
                    "gain": Gain.string[self.sensor.gain],
                    "astep": self.sensor.astep,
                    "atime": self.sensor.atime,
                    "tint": round(self.integration_time, 3),
                }
            ),
        }
        for channel in CONST["channels"]:
            raw_count = getattr(self.sensor, f"channel_{channel}")
            norm_count = self.normalize_count(raw_count)

            row[f"ch_{channel}_raw_count"] = raw_count
            row[f"ch_{channel}_norm_count"] = round(norm_count)

        return row

    def normalize_count(self, raw_count):
        # Adjust for gain
        gain_adjusted_count = raw_count * CONST["calibration_gain"] / Gain.string[self.sensor.gain]

        # Adjust for integration time
        time_adjusted_count = gain_adjusted_count * CONST["calibration_tint_ms"] / self.integration_time

        return time_adjusted_count
