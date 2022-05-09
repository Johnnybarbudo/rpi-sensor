import board
import adafruit_shtc3


def get_sensor():
    i2c = board.I2C()
    sensor = adafruit_shtc3.SHTC3(i2c)

    return sensor
