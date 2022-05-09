import board
import busio
from adafruit_ms8607 import MS8607


def get_sensor():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = MS8607(i2c)

    return sensor
