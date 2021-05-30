import board
import busio
import adafruit_sht31d


def get_sensor():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_sht31d.SHT31D(i2c)

    return sensor
