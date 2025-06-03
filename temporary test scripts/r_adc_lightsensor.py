import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA) # pin 5, pin 3
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P1)  # A1

print(f"Spannung: {chan.voltage:.2f} V")
