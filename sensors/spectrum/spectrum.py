import yaml
from pathlib import Path
from time import sleep
from datetime import datetime, timezone
from sensors.spectrum.as7341 import sensor
from sensors.spectrum.calibration import CALIBRATION, CONST
from adafruit_as7341 import Gain


class SpectrumSensor:
    def __init__(self):
        self.sensor = sensor
        self.sensor.gain = 7
        self.load_config()

    def update_tint(self):
        self.integration_time = ((self.sensor.atime + 1) * (self.sensor.astep + 1) * 2.78) / 1000
        print(f"Integration time: {round(self.integration_time, 2)} ms")

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
            "gain": Gain.string[self.sensor.gain],
            "astep": self.sensor.astep,
            "atime": self.sensor.atime,
            "tint": round(self.integration_time, 3),
        }
        for channel in CALIBRATION:
            raw_count = getattr(self.sensor, channel)
            norm_count = self.normalize_count(raw_count)
            irradiance_in_w_per_m2 = self.calc_irradiance(norm_count, channel)
            if "nm" in channel:
                pfd_in_micromols = self.calc_pfd(irradiance_in_w_per_m2, channel)
            else:
                pfd_in_micromols = None

            channel_short_name = channel.split("_")[1]
            row[f"ch_{channel_short_name}_raw_count"] = raw_count
            row[f"ch_{channel_short_name}_norm_count"] = round(norm_count)
            row[f"ch_{channel_short_name}_irrad"] = round(irradiance_in_w_per_m2, 3)

            # Skip for NIR and CLEAR where PFD is not calculated
            if pfd_in_micromols:
                row[f"ch_{channel_short_name}_pfd"] = round(pfd_in_micromols, 3)

        return row

    def normalize_count(self, raw_count):
        # Adjust for gain
        gain_adjusted_count = raw_count * 64 / Gain.string[self.sensor.gain]

        # Adjust for integration time
        time_adjusted_count = gain_adjusted_count * CONST["integration_ms"] / self.integration_time

        return time_adjusted_count

    def calc_irradiance(self, normalized_count, channel):
        # Get irradiance in microwatts / cm2
        irradiance_in_uw_per_cm2 = normalized_count * CONST["irradiance"] / CALIBRATION[channel]

        # Get irradiance in watts / m2
        irradiance_in_w_per_cm2 = irradiance_in_uw_per_cm2 / 1000000
        irradiance_in_w_per_m2 = irradiance_in_w_per_cm2 * 100 * 100

        return irradiance_in_w_per_m2

    def calc_pfd(self, irradiance_in_w_per_m2, channel):
        """
        Calculate Photon Flux Density
        """
        wavelength_in_meters = int(channel.split("_")[1].split("nm")[0]) / 1e9
        energy_of_1_photon = CONST["Planck"] * CONST["lightspeed"] / wavelength_in_meters
        photon_count = irradiance_in_w_per_m2 / energy_of_1_photon
        pfd_in_micromols = 1e6 * photon_count / CONST["Avogadro"]

        return pfd_in_micromols


# if channel == "channel_415nm":
#     print("raw_count", raw_count)
#     print("gain", Gain.string[self.sensor.gain])
#     b_gain_adjusted_counts = raw_count * 512 / Gain.string[self.sensor.gain]
#     print("b_gain_adjusted_counts", b_gain_adjusted_counts)
#     print("self.integration_time", self.integration_time)
#     b_time_adjusted_counts = b_gain_adjusted_counts * 100 / self.integration_time
#     print("b_time_adjusted_counts", b_time_adjusted_counts)
#     b_irradiance_in_uw_per_cm2 = b_time_adjusted_counts * 57 / 3200

#     w_gain_adjusted_counts = raw_count * 64 / Gain.string[self.sensor.gain]
#     w_time_adjusted_counts = w_gain_adjusted_counts * 27.8 / self.integration_time
#     w_irradiance_in_uw_per_cm2 = w_time_adjusted_counts * 107.67 / 55

#     print("BBBBBBBBB", round(w_irradiance_in_uw_per_cm2, 3), round(b_irradiance_in_uw_per_cm2, 3))

# if channel == "channel_NIR":
#     r_gain_adjusted_counts = raw_count * 128 / Gain.string[self.sensor.gain]
#     r_time_adjusted_counts = r_gain_adjusted_counts * 100 / self.integration_time
#     r_irradiance_in_uw_per_cm2 = r_time_adjusted_counts * 98 / 5135

#     w_gain_adjusted_counts = raw_count * 64 / Gain.string[self.sensor.gain]
#     w_time_adjusted_counts = w_gain_adjusted_counts * 27.8 / self.integration_time
#     w_irradiance_in_uw_per_cm2 = w_time_adjusted_counts * 107.67 / 55

#     print("RRRRRRRRRRR", round(w_irradiance_in_uw_per_cm2, 3), round(r_irradiance_in_uw_per_cm2, 3))
