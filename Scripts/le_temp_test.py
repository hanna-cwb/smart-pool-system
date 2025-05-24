import Adafruit_DHT
import time

# Sensor Configuration
SENSOR_TYPE = Adafruit_DHT.DHT11
GPIO_PIN = 4  # GPIO4 (physical pin 7)

# Main Loop
try:
    while True:
        temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, GPIO_PIN)

        if temperature is not None:
            print(f"Temperature: {temperature:.1f} °C")
        else:
            print("Sensor error: could not read data.")

        time.sleep(10)

except KeyboardInterrupt:
    print("Measurement stopped by user.")