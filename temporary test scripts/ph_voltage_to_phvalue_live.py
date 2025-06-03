import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# I2C-Verbindung starten
i2c = busio.I2C(board.SCL, board.SDA)

# ADS1115 initialisieren
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0)

# Kalibrierte Formel: 2.5 V = pH 7, 3.0 V = pH 4, 2.0 V = pH 10
def voltage_to_ph(voltage):
    ph = 7 - ((voltage - 2.5) * 6)
    return round(ph, 2)

print("Starte pH-Messung... (Drücke STRG+C zum Beenden)")

try:
    while True:
        voltage = chan.voltage
        ph_value = voltage_to_ph(voltage)
        print(f"Spannung: {voltage:.3f} V → geschätzter pH-Wert: {ph_value}")
        time.sleep(1)

except KeyboardInterrupt:
    print("Messung beendet.")