from sensors.hum_temp.shtc3 import get_sensor


class HumTempSensor:
    def __init__(self):
        self.sensor = get_sensor()

    def measure(self):
        row = {
            "humidity": round(self.sensor.relative_humidity, 3),
            "temperature": round(self.sensor.temperature, 3),
        }

        return row
