import time
import board
import busio
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT Configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/waterlevel"

# GPIO Setup
TRIG_PIN = 23
ECHO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Distance Measurement Function
def get_distance():
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    while GPIO.input(ECHO_PIN) == 0:
        start = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        stop = time.time()

    distance = (stop - start) * 34300 / 2
    return round(distance, 2)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker successfully")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    logging.info("Message published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")

mqttc.on_connect = on_connect

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_start()

    logging.info("Starting water level measurement...")

    try:
        while True:
            dist = get_distance()
            logging.info(f"Publishing: Distance = {dist} cm")
            mqttc.publish(MQTT_TOPIC, dist)
            time.sleep(2)

    except KeyboardInterrupt:
        logging.info("Measurement stopped by user.")

    mqttc.loop_stop()
    mqttc.disconnect()

except Exception as e:
    logging.error(f"Error: {e}")
finally:
    GPIO.cleanup()
