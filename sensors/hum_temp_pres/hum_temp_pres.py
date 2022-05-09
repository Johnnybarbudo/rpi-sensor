from datetime import datetime, timezone
from sensors.hum_temp_pres.ms8607 import get_sensor


class HumTempPresSensor:
    def __init__(self):
        self.sensor = get_sensor()

    def measure(self):
        row = {
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "humidity": round(self.sensor.relative_humidity, 3),
            "temperature": round(self.sensor.temperature, 3),
            "pressure": round(self.sensor.pressure, 3),
        }

        return row
