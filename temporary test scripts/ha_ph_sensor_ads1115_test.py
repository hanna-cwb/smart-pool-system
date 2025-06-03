import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# I2C-Verbindung starten
i2c = busio.I2C(board.SCL, board.SDA)

# ADS1115 initialisieren
ads = ADS.ADS1115(i2c)

# Kanal A0 für pH-Sensor (Po-Pin)
channel = AnalogIn(ads, ADS.P0)

print("Starte Messung vom pH-Sensor (Po → A0)...")
print("Drücke STRG+C zum Beenden.")

try:
    while True:
        voltage = channel.voltage
        print(f"Gemessene Spannung: {voltage:.3f} V")
        time.sleep(1)

except KeyboardInterrupt:
    print("Messung beendet.")