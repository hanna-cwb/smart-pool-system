import Adafruit_DHT
import time
import paho.mqtt.client as mqtt
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Sensor Configuration
SENSOR_TYPE = Adafruit_DHT.DHT11
GPIO_PIN = 4  # GPIO4 = Pin 7

# MQTT Configuration
MQTT_HOST = "192.168.8.137"  
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/temperature"

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker successfully")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    logging.info("Temperature published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.username_pw_set(username="mqtt-user", password="mqtt")

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_start()

    temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, GPIO_PIN)

    if temperature is not None:
        message = f"{temperature:.1f}"
        logging.info(f"Publishing temperature: {message} °C")
        mqttc.publish(MQTT_TOPIC, message)
    else:
        logging.warning("Failed to read from DHT11 sensor.")

    time.sleep(10)

except KeyboardInterrupt:
    logging.info("Stopped by user.")
    mqttc.loop_stop()
    mqttc.disconnect()

except Exception as e:
    logging.error(f"Error: {e}")