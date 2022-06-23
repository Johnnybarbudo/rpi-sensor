import numpy as np
from sched import scheduler
from time import time, sleep
from datetime import datetime
from sensors.spectrum.spectrum import SpectrumSensor
from sensors.hum_temp.hum_temp import HumTempSensor
from sensors.hum_temp_pres.hum_temp_pres import HumTempPresSensor
from publisher import Publisher


class Main:
    def __init__(self):
        print("Starting data acquisition")
        self.publisher = Publisher()
        self.sensors = {}
        self.results = {}
        self.sensor_factories = {"SPECTRUM": SpectrumSensor, "HUM_TEMP": HumTempSensor, "HUM_TEMP_PRES": HumTempPresSensor}

        for data_type in self.publisher.enabled_sensors:
            self.results[data_type] = []
            self.sensors[data_type] = self.sensor_factories[data_type]()

        self.measurement_cycle_length = self.publisher.measurement_cycle_length
        self.submit_after_cycles = self.publisher.submit_after_cycles
        self.loops_executed = 0
        self.run()

    def run(self):
        try:
            self.scheduler = scheduler(time, sleep)
            self.scheduler.enter(0, 1, self.get_data, (time(),))
            self.scheduler.run()
        except KeyboardInterrupt:
            print(" Exiting Scheduler loop")

    def get_data(self, t):
        # Schedule next iteration self.measurement_cycle_length seconds later
        # Start with this, so the time it takes to take measurements and submit them won't be added to the delay
        self.scheduler.enterabs(t + self.measurement_cycle_length, 1, self.get_data, (t + self.measurement_cycle_length,))

        # Take measurements on all sensors
        start_time = time()
        for data_type in self.publisher.enabled_sensors:
            result = self.sensors[data_type].measure()
            self.results[data_type].append(result)
        end_time = time()

        # Print a warning if the time it took to take measurements is longer than the cycle time
        if (end_time - start_time) * 1000 > self.measurement_cycle_length * 1000:
            start_ms = round((end_time - start_time) * 1000, 2)
            end_ms = self.measurement_cycle_length * 1000
            print(f"WARNING: measurement loop execution time ({start_ms}ms) exceeded measurement_cycle_length ({end_ms}ms)!")

        # Check if the accumulated measurements exceed the threshold, and submit them if they do
        # Just use the last result type (self.results[data_type]), but all should have the same length
        if len(self.results[data_type]) >= self.submit_after_cycles:
            self.submit_data()

    def submit_data(self):
        # Submit measurements for each data tye
        for data_type in self.results:
            # Calculate mean of the accumulated data points
            result = {"timestamp": datetime.now()}
            print(self.results)
            if data_type == "SPECTRUM":
                bands = self.results["SPECTRUM"][0].keys()
                values_per_bands = {}
                for band in bands:
                    values_per_bands[band] = [x[band] for x in self.results["SPECTRUM"]]

                for band in values_per_bands:
                    result[band] = np.array(values_per_bands[band]).mean(axis=0)
            else:
                result[data_type] = np.mean(self.results[data_type], axis=0)
            # Submit the mean
            print("result", result)
            self.publisher.publish([result], data_type)
            print(f"'{data_type}' published.")
            # Reset accumulator
            self.results[data_type] = []


Main()
