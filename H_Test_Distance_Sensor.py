import time
import board
import busio
import adafruit_vl6180x

# I2C-Bus initialisieren (Raspberry Pi verwendet I2C-1)
i2c = busio.I2C(board.SCL, board.SDA)

# Sensor initialisieren
sensor = adafruit_vl6180x.VL6180X(i2c)

print("Starte Messung...")

try:
    while True:
        # Abstand in Millimeter messen
        distance = sensor.range
        print(f"Entfernung: {distance} mm")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nMessung beendet.")
