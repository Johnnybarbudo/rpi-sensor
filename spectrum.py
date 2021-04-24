from time import sleep
import board
import busio
from adafruit_as7341 import AS7341

i2c = busio.I2C(board.SCL, board.SDA)
sensor = AS7341(i2c)
# print([method_name for method_name in dir(sensor) if callable(getattr(sensor, method_name))])


def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")


def channel_CLEAR():
    """The current reading for the CLEAR band"""
    sensor._configure_f5_f8()
    return sensor._channel_4_data


def channel_NIR():
    """The current reading for the NIR band"""
    sensor._configure_f5_f8()
    return sensor._channel_5_data


while True:
    sensor_channels = sensor.all_channels
    print(sensor_channels)

    print("F01 - 415nm/Violet  %s" % bar_graph(sensor.channel_415nm))
    print("F02 - 445nm//Indigo %s" % bar_graph(sensor.channel_445nm))
    print("F03 - 480nm//Blue   %s" % bar_graph(sensor.channel_480nm))
    print("F04 - 515nm//Cyan   %s" % bar_graph(sensor.channel_515nm))
    print("F05 - 555nm/Green   %s" % bar_graph(sensor.channel_555nm))
    print("F06 - 590nm/Yellow  %s" % bar_graph(sensor.channel_590nm))
    print("F07 - 630nm/Orange  %s" % bar_graph(sensor.channel_630nm))
    print("F08 - 680nm/Red     %s" % bar_graph(sensor.channel_680nm))
    print("F09 - CLEAR         %s" % bar_graph(channel_CLEAR()))
    print("F10 - NIR           %s" % bar_graph(channel_NIR()))
    print("\n------------------------------------------------")
    sleep(1)
