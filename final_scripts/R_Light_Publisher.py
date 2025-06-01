import time
import board
import busio
import paho.mqtt.client as mqtt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/light"

# Threshold for light detection in volt
DARKNESS_THRESHOLD = 1.1

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
analog_channel = AnalogIn(ads, ADS.P1) # A1

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker successfully")
    else:
        logging.error(f"Connection failed, return code: {rc}")

def on_publish(client, userdata, mid):
    logging.info("Message published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_start()

    logging.info("Starting light level monitoring...")

    last_state = None

    while True:
        voltage = analog_channel.voltage
        logging.info(f"Measured voltage: {voltage:.3f} V")

        if voltage > DARKNESS_THRESHOLD and last_state != "on":
            mqttc.publish(MQTT_TOPIC, "on")
            logging.info("It's dark: sending LIGHT ON")
            last_state = "on"
        elif voltage <= DARKNESS_THRESHOLD and last_state != "off":
            mqttc.publish(MQTT_TOPIC, "off")
            logging.info("It's bright enough: sending LIGHT OFF")
            last_state = "off"

        time.sleep(2)

except KeyboardInterrupt:
    logging.info("Measurement stopped by user")
    mqttc.loop_stop()
    mqttc.disconnect()
except Exception as e:
    logging.error(f"Error: {e}")
