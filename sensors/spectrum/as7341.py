import board
import busio
from adafruit_as7341 import AS7341


# Add missing CLEAR and NIR accessors
def channel_CLEAR(self):
    """The current reading for the CLEAR band"""
    self._configure_f5_f8()
    return self._channel_4_data


def channel_NIR(self):
    """The current reading for the NIR band"""
    self._configure_f5_f8()
    return self._channel_5_data


def get_sensor():
    AS7341.channel_CLEAR = property(channel_CLEAR)
    AS7341.channel_NIR = property(channel_NIR)

    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = AS7341(i2c)

    return sensor
