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

# Initialize I2C-Bus 
i2c = busio.I2C(board.SCL, board.SDA)
# Initialize Sensor
sensor = adafruit_vl6180x.VL6180X(i2c)

# Define on_connect event Handler
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker successfully")
    else:
        logging.error(f"Failed to connect, return code {rc}")

# Define on_publish event Handler
def on_publish(client, userdata, mid):
    logging.info("Message Published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")

# Register Event Handlers
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

try:
    # Connect to MQTT Broker
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

    # Start MQTT loop to handle callbacks
    mqttc.loop_start()

    print("Start distance measuring...")

    try:
      while True: 
          # Measaure distance in mm
          distance = sensor.range
          print(f"Distance: {distance} mm")

          if distance < 50:
              message = "Capture"
              mqttc.publish(MQTT_TOPIC, message)

          time.sleep(1)
    except KeyboardInterrupt:
      print("\nDistance measuring stopped.")

    # Give some time for message to be sent before disconnecting
    mqttc.loop_stop()
    mqttc.disconnect()

except Exception as e:
    logging.error(f"Error: {e}")
