from sched import scheduler
from time import time, sleep
from sensors.spectrum.spectrum import SpectrumSensor
from sensors.hum_temp.hum_temp import HumTempSensor
from publisher import Publisher


class Main:
    def __init__(self):
        print("Starting data acquisition")
        self.publisher = Publisher()
        self.sensors = {}
        self.results = {}
        self.sensor_factories = {"SPECTRUM": SpectrumSensor, "HUM_TEMP": HumTempSensor}

        for data_type in self.publisher.enabled_sensors:
            self.results[data_type] = []
            self.sensors[data_type] = self.sensor_factories[data_type]()

        self.period_length = self.publisher.period_length
        self.batch_size = self.publisher.batch_size
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
        # Execute current iteration
        start_time = time()
        for data_type in self.publisher.enabled_sensors:
            result = self.sensors[data_type].measure()
            self.results[data_type].append(result)
        end_time = time()

        if (end_time - start_time) * 1000 > self.period_length * 1000:
            start_ms = round((end_time - start_time) * 1000, 2)
            end_ms = self.period_length * 1000
            print(f"WARNING: measurement loop execution time ({start_ms}ms) exceeded period_length ({end_ms}ms)!")

        self.loops_executed += 1
        if (self.loops_executed % self.batch_size) == 0:
            self.submit_data()

        # Schedule next iteration self.period_length seconds later
        self.scheduler.enterabs(t + self.period_length, 1, self.get_data, (t + self.period_length,))

    def submit_data(self):
        for data_type in self.results:
            self.publisher.publish(self.results[data_type], data_type)
            print(f"{len(self.results[data_type])} rows published of data_type: {data_type}")
            self.results[data_type] = []


Main()
