import time
import adafruit_dht
import board
import paho.mqtt.client as mqtt

# MQTT-Konfiguration
MQTT_BROKER = "192.168.8.137" 
MQTT_PORT = 1883
MQTT_TOPIC_TEMP = "/sensor/temperature"
MQTT_TOPIC_HUM = "/sensor/humidity"

# Initialisiere DHT11 (GPIO4)
sensor = adafruit_dht.DHT22(board.D4)

# MQTT-Client initialisieren und verbinden
client = mqtt.Client()
client.username_pw_set(username="mqtt-user", password="mqtt")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()  # falls du später auch Nachrichten empfangen willst

try:
    while True:
        try:
            temp = sensor.temperature
            hum = sensor.humidity

            if temp is not None and hum is not None:
                temperature_c = sensor.temperature
                temperature_f = temperature_c * (9 / 5) + 32
                humidity = sensor.humidity
                print("Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))
                client.publish(MQTT_TOPIC_TEMP, temp)
                client.publish(MQTT_TOPIC_HUM, hum)
            else:
                print("Sensor liefert keine Werte")

        except RuntimeError as e:
            print(f"Sensorfehler: {e}")
        time.sleep(5)

except KeyboardInterrupt:
    print("Beende Programm...")
    client.loop_stop()
    client.disconnect()
