import time
import adafruit_dht
import board
import paho.mqtt.client as mqtt
import logging

# MQTT Configuration
MQTT_BROKER = "192.168.8.137" 
MQTT_PORT = 1883
MQTT_TOPIC_TEMP = "/sensor/temperature"
MQTT_TOPIC_HUM = "/sensor/humidity"

# Initialize temperature sensor DHT11 (GPIO4)
sensor = adafruit_dht.DHT22(board.D4)

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker successfully")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    logging.info("Temperature published successfully")

# Initialize MQTT-Client 
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.username_pw_set(username="mqtt-user", password="mqtt")

try:
    mqttc.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqttc.loop_start()

    while True:
        try:
            temp = sensor.temperature
            hum = sensor.humidity

            if temp is not None and hum is not None:
                temperature_c = sensor.temperature
                temperature_f = temperature_c * (9 / 5) + 32
                humidity = sensor.humidity
                print("Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))
                mqttc.publish(MQTT_TOPIC_TEMP, temp)
                mqttc.publish(MQTT_TOPIC_HUM, hum)
            else:
                print("No values detected")

        except RuntimeError as e:
            print(f"Sensor error: {e}")
        time.sleep(5)

except KeyboardInterrupt:
    logging.info("Measurement stopped by user.")
except Exception as e:
    logging.error(f"MQTT Error: {e}")
finally:
    mqttc.loop_stop()
    mqttc.disconnect()
