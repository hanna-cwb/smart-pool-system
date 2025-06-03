import time
import board
import busio
import adafruit_vl6180x
import paho.mqtt.client as mqtt
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT Configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/distance"

# Threshold for motion detection in mm
DISTANCE_THRESHOLD = 50

# Initialize I2C-Bus 
i2c = busio.I2C(board.SCL, board.SDA)
# Initialize Sensor
sensor = adafruit_vl6180x.VL6180X(i2c)

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Connection failed with return code {rc}")

def on_publish(client, userdata, mid):
    logging.info("Message Published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")

mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_start()

    print("Start distance measuring...")

    while True: 
        # Measure distance in mm
        distance = sensor.range
        print(f"Distance: {distance} mm")
        message = ""
        if distance < DISTANCE_THRESHOLD:
            message = "Capture"
        else:
            message = "No motion detected"

        mqttc.publish(MQTT_TOPIC, message)
        time.sleep(1)

except KeyboardInterrupt:
    logging.info("Measurement stopped by user.")
except Exception as e:
    logging.error(f"MQTT Error: {e}")
finally:
    mqttc.loop_stop()
    mqttc.disconnect()
