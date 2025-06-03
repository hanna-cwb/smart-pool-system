import adafruit_dht
import board
import time

# liefert keine sinnvollen Werte !!!!
# DHT11 auf GPIO4
sensor = adafruit_dht.DHT11(board.D4)

while True:
    try:
        temperature = sensor.temperature
        humidity = sensor.humidity
        print(f"Temp: {temperature}°C | Feuchtigkeit: {humidity}%")
    except RuntimeError as e:
        print(f"Fehler: {e}")
    time.sleep(2)
